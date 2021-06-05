import time
import torch
import pysbd
import librosa
import soundfile as sf
import numpy as np
import scipy.io.wavfile

from TTS.tts.utils.visual import plot_spectrogram
from TTS.utils.io import load_config
from TTS.tts.utils.speakers import load_speaker_mapping
from TTS.vocoder.utils.generic_utils import setup_generator, interpolate_vocoder_input
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
from TTS.tts.utils.synthesis import *

from TTS.tts.utils.text import make_symbols, phonemes, symbols
from tacotron2 import Tacotron2


# import pyworld as pw


# pylint: disable=too-many-public-methods
class AudioProcessor(object):
    def __init__(self,
                 sample_rate=None,
                 resample=False,
                 min_level_db=None,
                 ref_level_db=None,
                 signal_norm=None,
                 symmetric_norm=None,
                 max_norm=None,
                 clip_norm=True,
                 do_sound_norm=False,
                 stats_path=None,
                 verbose=True,
                 **_):

        # setup class attributed
        self.sample_rate = sample_rate
        self.resample = resample

        self.min_level_db = min_level_db or 0

        self.ref_level_db = ref_level_db

        self.signal_norm = signal_norm
        self.symmetric_norm = symmetric_norm
        self.max_norm = 1.0 if max_norm is None else float(max_norm)
        self.clip_norm = clip_norm
        self.do_sound_norm = do_sound_norm
        # setup stft parameters
        assert min_level_db != 0.0, " [!] min_level_db is 0"
        members = vars(self)
        if verbose:
            print(" > Setting up Audio Processor...")
            for key, value in members.items():
                print(" | > {}:{}".format(key, value))
        # create spectrogram utils
        self.mel_basis = self._build_mel_basis()
        self.inv_mel_basis = np.linalg.pinv(self._build_mel_basis())
        # setup scaler
        if stats_path:
            mel_mean, mel_std, linear_mean, linear_std, _ = self.load_stats(stats_path)
            self.setup_scaler(mel_mean, mel_std, linear_mean, linear_std)
            self.signal_norm = True
            self.max_norm = None
            self.clip_norm = None
            self.symmetric_norm = None

    def denormalize(self, S):
        """denormalize values"""
        # pylint: disable=no-else-return
        S_denorm = S.copy()
        if self.signal_norm:
            # mean-var scaling
            if hasattr(self, 'mel_scaler'):
                if S_denorm.shape[0] == self.num_mels:
                    return self.mel_scaler.inverse_transform(S_denorm.T).T
                elif S_denorm.shape[0] == self.fft_size / 2:
                    return self.linear_scaler.inverse_transform(S_denorm.T).T
                else:
                    raise RuntimeError(' [!] Mean-Var stats does not match the given feature dimensions.')
            if self.symmetric_norm:
                if self.clip_norm:
                    S_denorm = np.clip(S_denorm, -self.max_norm,
                                       self.max_norm)  # pylint: disable=invalid-unary-operand-type
                S_denorm = ((S_denorm + self.max_norm) * -self.min_level_db / (2 * self.max_norm)) + self.min_level_db
                return S_denorm + self.ref_level_db
            else:
                if self.clip_norm:
                    S_denorm = np.clip(S_denorm, 0, self.max_norm)
                S_denorm = (S_denorm * -self.min_level_db /
                            self.max_norm) + self.min_level_db
                return S_denorm + self.ref_level_db
        else:
            return S_denorm

    ### Mean-STD scaling ###
    def load_stats(self, stats_path):
        stats = np.load(stats_path, allow_pickle=True).item()  # pylint: disable=unexpected-keyword-arg
        mel_mean = stats['mel_mean']
        mel_std = stats['mel_std']
        linear_mean = stats['linear_mean']
        linear_std = stats['linear_std']
        stats_config = stats['audio_config']
        # check all audio parameters used for computing stats
        skip_parameters = ['griffin_lim_iters', 'stats_path', 'do_trim_silence', 'ref_level_db', 'power']
        for key in stats_config.keys():
            if key in skip_parameters:
                continue
            if key not in ['sample_rate', 'trim_db']:
                assert stats_config[key] == self.__dict__[key], \
                    f" [!] Audio param {key} does not match the value used for computing mean-var stats. {stats_config[key]} vs {self.__dict__[key]}"
        return mel_mean, mel_std, linear_mean, linear_std, stats_config

    @staticmethod
    def sound_norm(x):
        return x / abs(x).max() * 0.9

    ### save and load ###
    def load_wav(self, filename, sr=None):
        if self.resample:
            x, sr = librosa.load(filename, sr=self.sample_rate)
        elif sr is None:
            x, sr = sf.read(filename)
            assert self.sample_rate == sr, "%s vs %s" % (self.sample_rate, sr)
        else:
            x, sr = librosa.load(filename, sr=sr)

        if self.do_sound_norm:
            x = self.sound_norm(x)
        return x

    def save_wav(self, wav, path):
        wav_norm = wav * (32767 / max(0.01, np.max(np.abs(wav))))
        scipy.io.wavfile.write(path, self.sample_rate, wav_norm.astype(np.int16))


class Synthesizer(object):
    def __init__(self, tts_checkpoint, tts_config, vocoder_checkpoint=None, vocoder_config=None, use_cuda=False):
        """Encapsulation of tts and vocoder models for inference.

        TODO: handle multi-speaker and GST inference.

        Args:
            tts_checkpoint (str): path to the tts model file.
            tts_config (str): path to the tts config file.
            vocoder_checkpoint (str, optional): path to the vocoder model file. Defaults to None.
            vocoder_config (str, optional): path to the vocoder config file. Defaults to None.
            use_cuda (bool, optional): enable/disable cuda. Defaults to False.
        """
        self.tts_checkpoint = tts_checkpoint
        self.tts_config = tts_config
        self.vocoder_checkpoint = vocoder_checkpoint
        self.vocoder_config = vocoder_config
        self.use_cuda = use_cuda
        self.wavernn = None
        self.vocoder_model = None
        self.num_speakers = 0
        self.tts_speakers = None
        self.speaker_embedding_dim = None
        self.seg = self.get_segmenter("en")
        self.use_cuda = use_cuda
        if self.use_cuda:
            assert torch.cuda.is_available(), "CUDA is not availabe on this machine."
        self.load_tts(tts_checkpoint, tts_config,
                      use_cuda)
        if vocoder_checkpoint:
            self.load_vocoder(vocoder_checkpoint, vocoder_config, use_cuda)

    @staticmethod
    def get_segmenter(lang):
        return pysbd.Segmenter(language=lang, clean=True)

    def load_speakers(self):
        # load speakers
        if self.model_config.use_speaker_embedding is not None:
            self.tts_speakers = load_speaker_mapping(self.tts_config.tts_speakers_json)
            self.num_speakers = len(self.tts_speakers)
        else:
            self.num_speakers = 0
        # set external speaker embedding
        if self.tts_config.use_external_speaker_embedding_file:
            speaker_embedding = self.tts_speakers[list(self.tts_speakers.keys())[0]]['embedding']
            self.speaker_embedding_dim = len(speaker_embedding)

    def init_speaker(self, speaker_idx):
        # load speakers
        speaker_embedding = None
        if hasattr(self, 'tts_speakers') and speaker_idx is not None:
            assert speaker_idx < len(
                self.tts_speakers), f" [!] speaker_idx is out of the range. {speaker_idx} vs {len(self.tts_speakers)}"
            if self.tts_config.use_external_speaker_embedding_file:
                speaker_embedding = self.tts_speakers[speaker_idx]['embedding']
        return speaker_embedding

    def load_tts(self, tts_checkpoint, tts_config, use_cuda):
        # pylint: disable=global-statement
        global symbols, phonemes

        self.tts_config = load_config(tts_config)
        self.use_phonemes = self.tts_config.use_phonemes
        self.ap = AudioProcessor(**self.tts_config.audio)

        if 'characters' in self.tts_config.keys():
            symbols, phonemes = make_symbols(**self.tts_config.characters)

        if self.use_phonemes:
            self.input_size = len(phonemes)
        else:
            self.input_size = len(symbols)

        self.tts_model = Tacotron2(num_chars=num_chars + getattr(c, "add_blank", False),
                                   num_speakers=num_speakers,
                                   r=c.r,
                                   postnet_output_dim=c.audio['num_mels'],
                                   decoder_output_dim=c.audio['num_mels'],
                                   gst=c.use_gst,
                                   gst_embedding_dim=c.gst['gst_embedding_dim'],
                                   gst_num_heads=c.gst['gst_num_heads'],
                                   gst_style_tokens=c.gst['gst_style_tokens'],
                                   gst_use_speaker_embedding=c.gst['gst_use_speaker_embedding'],
                                   attn_type=c.attention_type,
                                   attn_win=c.windowing,
                                   attn_norm=c.attention_norm,
                                   prenet_type=c.prenet_type,
                                   prenet_dropout=c.prenet_dropout,
                                   forward_attn=c.use_forward_attn,
                                   trans_agent=c.transition_agent,
                                   forward_attn_mask=c.forward_attn_mask,
                                   location_attn=c.location_attn,
                                   attn_K=c.attention_heads,
                                   separate_stopnet=c.separate_stopnet,
                                   bidirectional_decoder=c.bidirectional_decoder,
                                   double_decoder_consistency=c.double_decoder_consistency,
                                   ddc_r=c.ddc_r,
                                   speaker_embedding_dim=speaker_embedding_dim)
        self.tts_model.load_checkpoint(tts_config, tts_checkpoint, eval=True)
        if use_cuda:
            self.tts_model.cuda()

    def load_vocoder(self, model_file, model_config, use_cuda):
        self.vocoder_config = load_config(model_config)
        self.vocoder_ap = AudioProcessor(**self.vocoder_config['audio'])
        self.vocoder_model = setup_generator(self.vocoder_config)
        self.vocoder_model.load_checkpoint(self.vocoder_config, model_file, eval=True)
        if use_cuda:
            self.vocoder_model.cuda()

    def save_wav(self, wav, path):
        wav = np.array(wav)
        self.ap.save_wav(wav, path)

    def split_into_sentences(self, text):
        return self.seg.segment(text)

    def tts(self, text, speaker_idx=None):
        start_time = time.time()
        wavs = []
        sens = self.split_into_sentences(text)
        print(" > Text splitted to sentences.")
        print(sens)

        speaker_embedding = None
        use_gl = False

        for sen in sens:
            # synthesize voice
            _, _, mel_postnet_spec, _, _ = synthesis(
                self.tts_model,
                sen,
                self.tts_config,
                self.use_cuda,
                self.ap,
                do_trim_silence=True,
                enable_eos_bos_chars=self.tts_config.enable_eos_bos_chars
            )

            # denormalize tts output based on tts audio config
            mel_postnet_spec = self.ap.denormalize(mel_postnet_spec.T).T
            device_type = "cuda" if self.use_cuda else "cpu"
            # renormalize spectrogram based on vocoder config
            vocoder_input = self.vocoder_ap.normalize(mel_postnet_spec.T)
            # compute scale factor for possible sample rate mismatch
            spec_fig = plot_spectrogram(mel_postnet_spec)
            spec_fig.savefig('/home/fypgantts/StyleTTS/spectrograms/' + sen + '.PNG')
            scale_factor = [1, self.vocoder_config['audio']['sample_rate'] / self.ap.sample_rate]
            if scale_factor[1] != 1:
                print(" > interpolating tts model output.")
                vocoder_input = interpolate_vocoder_input(scale_factor, vocoder_input)
            else:
                vocoder_input = torch.tensor(vocoder_input).unsqueeze(0)  # pylint: disable=not-callable
            # run vocoder model
            # [1, T, C]
            waveform = self.vocoder_model.inference(vocoder_input.to(device_type))
            if self.use_cuda:
                waveform = waveform.cpu()

            waveform = waveform.numpy()
            waveform = waveform.squeeze()

            # trim silence
            waveform = trim_silence(waveform, self.ap)

            wavs += list(waveform)
            wavs += [0] * 10000

        # compute stats
        process_time = time.time() - start_time
        audio_time = len(wavs) / self.tts_config.audio['sample_rate']
        print(f" > Processing time: {process_time}")
        print(f" > Real-time factor: {process_time / audio_time}")
        return wavs
