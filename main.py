from os import listdir
from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer
# from nltk.wordnet import WordNetLemmatizer
from tqdm import tqdm
from math import sqrt
import re
import copy

my_re = re.compile("[a-zA-Z]+-{0,1}'{0,1}[a-zA-z]*")



# global

stemmer = SnowballStemmer(language='english')

stop_list = {}


def populate_stoplist(file_name):
    global stop_list
    try:
        with open(file_name) as stoplist_file:
            words = stoplist_file.read()
    except:
        print("Incorrect stoplist file path")
        exit(-1)
    stop_list = {word: True for word in words.split("\n")}


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
    global stop_list

    for index, token in enumerate(my_re.findall(document)):
        text = token.lower()

        if not (stop_list.get(text, False) or stop_list.get(stemmer.stem(text))):

            text = stemmer.stem(text)
            if token_positioning.get(text, False):
                token_positioning[text]["positions"].append(index - token_positioning[text]["positions"][-1])
                token_positioning[text]["tf"] += 1
            else:
                token_positioning[text] = {"positions": [index], "tf": 1}

    return token_positioning


def pre_processing(document: str):

    document = document_parser(document)
    tokens = my_tokenizer(document)

    return tokens


# create inverted index from a single document
def inverter(tokens, doc_id):
    inverted_index = {}
    for key in tokens.keys():
        inverted_index[key] = {}
        inverted_index[key][doc_id] = tokens[key]
        inverted_index[key]["df"] = 1
    inverted_index = dict(sorted(inverted_index.items()))

    return inverted_index


def merge_index(inverted_index, invt_ind):
    if not inverted_index:
        return  invt_ind
    else:
        for key in invt_ind.keys():
            if inverted_index.get(key, False):
                for doc_id in invt_ind[key].keys():
                    if doc_id != 'df':
                        if inverted_index[key].get(doc_id, False):

                            inverted_index[key][doc_id]["tf"] += invt_ind[key][doc_id]["tf"]
                            inverted_index[key][doc_id]["positions"].extend(invt_ind[key][doc_id]["positions"])

                        else:
                            inverted_index[key][doc_id] = invt_ind[key][doc_id]
                            inverted_index[key]["df"] += 1
            else:
                inverted_index[key] = invt_ind[key]
    inverted_index = dict(sorted(inverted_index.items()))

    return inverted_index


def store_doc_info(doc_info,directory: str, doc_name: str, tokens: dict):
    tok_freqs = [token_info["tf"] for token_info in tokens.values()]
    sum_squares = sum(tf * tf for tf in tok_freqs)
    doc_len = sum(tok_freqs)
    doc_mag = sqrt(sum_squares)

    doc_info.write(f"{doc_id},{dir}/{doc_name},{doc_len},{doc_mag}\n")


"""
Input: Iterators of both posting list to be intersected

"""


def intersect(posting1: iter, posting2: iter):
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


# Takes a directory of input files and creates an inverted index for them
def create_inverted_index(directory, doc_id ):
    # with open("Docinfo.txt", "a+") as doc_info:
    inverted_index = {}
    documents = listdir(directory)
    for document in tqdm(documents[:10]):
        with open(f"{directory}/{document}") as file:
            # print(f"{folder + dirs}/{document}")
            try:
                doc = file.read()
            except:
                print("file reading opsie")
                continue

            tokens = pre_processing(doc)
            inverted = inverter(tokens, doc_id)
            inverted_index = merge_index(inverted_index, inverted)
        # store_doc_info(doc_info, dirs, doc_id, document, tokens)

        doc_id += 1

    return inverted_index, doc_id
    # doc_info.close()


if __name__ == "__main__":
    doc_id = 1
    doc = ""
    populate_stoplist("stoplist.txt")
    index , doc_id= create_inverted_index("1", doc_id)
    print(index)
