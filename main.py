from os import listdir
from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer
# from nltk.wordnet import WordNetLemmatizer
from tqdm import tqdm
from math import sqrt
import re

my_re = re.compile("[a-zA-Z]+-{0,1}'{0,1}[a-zA-z]*")

# global
stop_list = []
stemmer = SnowballStemmer(language='english')


class PostingList:

    def __init__(self):
        self.df = 0
        self.postings = []  # list of dictionaries containing posting information
        # format {"doc_id":0, "tf":0, "term_positions":[]}

    def __len__(self):
        return len(self._postings)

    def __getitem__(self, position: int):
        # returning both doc id and term information for future use
        return self.postings[position]["doc_id"], self.postings[position]

    def __add__(self, posting: dict):
        self.postings.append(posting)
        self.df += 1

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.postings):
            return self[self.index]
        else:
            return None

    def decompressor(file, len: int):
        posting = {"doc_id": 0, "tf": 0, "term_positions": []}
        doc_completed = False
        for _ in range(len):
            # update self.df and rest of the things
            file.read(1)
            if doc_completed:
                yield posting

    def read_from_compressed_fileobj(self, file, start, end):
        file.seek(start)
        for posting in self.decompressor(file, start - end):
            self.postings.append(posting)

    def read_from_uncompressed_fileobj(self, file, start):
        pass


def document_parser(document: str):
    soup = BeautifulSoup(document)
    parsed_document = soup.get_text()

    return parsed_document


def my_tokenizer(document: str):
    token_positioning = {}
    positions_list = []
    for index, token in enumerate(my_re.findall(document)):
        text = token.lower()

        if text not in stop_list:
            text = stemmer.stem(text)
            if token_positioning.get(text, False):
                token_positioning[text]["positioning"].append(index - token_positioning[text]["positioning"][-1])
                token_positioning[text]["tf"] += 1
            else:
                token_positioning[text] = {"positioning": [index], "tf": 1}

    return token_positioning


def pre_processing(document: str):
    document = document_parser(document)
    tokens = my_tokenizer(document)

    return tokens


def store_doc_info(doc_info, dir: str, doc_id: int, doc_name: str, tokens: dict):
    tok_freqs = [token_info["tf"] for token_info in tokens.values()]
    sum_squares = sum(tf * tf for tf in tok_freqs)
    doc_len = sum(tok_freqs)
    doc_mag = sqrt(sum_squares)

    doc_info.write(f"{doc_id},{dir}/{doc_name},{doc_len},{doc_mag}\n")


"""
Input: Iterators of both posting list to be intersected

"""


def intersect(posting1: iter(), posting2: iter()):
    common_documents = []
    posting1_doc, _ = next(posting1)
    posting2_doc, _ = next(posting2)
    while posting1_doc is not None and posting2_doc is not None:
        if posting1_doc == posting2_doc:
            common_documents.append(posting1_doc)
        elif posting1_doc > posting2_doc:
            posting2_doc, _ = next(posting2)
        else:
            posting1_doc, _ = next(posting1)
    return common_documents


if __name__ == "__main__":

    dir_names = ["1", "2", "3"]
    doc_id = 1
    doc = ""
    with open("Docinfo.txt", "a+") as doc_info:
        for dirs in dir_names:
            for document in tqdm(listdir(dirs)):
                with open(f"{dirs}/{document}") as file:
                    # print(f"{folder + dirs}/{document}")
                    try:
                        doc = file.read()
                    except:
                        print("file reading opsie")
                        continue
                    tokens = pre_processing(doc)
                    store_doc_info(doc_info, dirs, doc_id, document, tokens)

                doc_id += 1
    doc_info.close()

    # file_list = listdir("1")
    # file_name = file_list[136]
    # with open ("1/" + file_name) as doc:
    #     file = document_parser(doc.read())
    # doc.close()
    # tokens = token_time(segmenter.normalize_and_segment, file)#my_tokenizer(file)
    # print(tokens)
    # print(len(tokens))
    # print(e.logtime_data)
