from os import listdir
from bs4 import BeautifulSoup
from tokenizer import tokenize, TOK
from nltk.stem.snowball import SnowballStemmer
#from nltk.wordnet import WordNetLemmatizer
from tqdm import tqdm
from math import sqrt
import re

my_re = re.compile("[a-zA-Z]+-[a-zA-Z]+|[a-zA-Z]+'{0,1}[a-zA-Z]{0,1}")




#global 
stop_list = []
stemmer = SnowballStemmer(language ='english')

def document_parser(document):
    soup = BeautifulSoup(document)
    parsed_document = soup.get_text()

    return parsed_document


def my_tokenizer(document):

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
                token_positioning[text] = {"positioning":[index] , "tf":1}

    return token_positioning


def pre_processing(document):

    document = document_parser(document)
    tokens = my_tokenizer(document)

    return tokens

def store_doc_info(dir, doc_id, doc_name,tokens):

    tok_freqs = [token_info["tf"] for token_info in tokens.values()]
    sum_squares = sum(tf*tf for tf in tok_freqs)
    doc_len = sum(tok_freqs)
    doc_mag = sqrt(sum_squares)
    #print("here")

    with open("Inverted-Index/Docinfo.txt", "a+") as doc_info:
        doc_info.write(f"{doc_id},{dir}/{doc_name},{doc_len},{doc_mag}\n")
    doc_info.close()




if __name__ == "__main__":

    folder = "Inverted-Index/"
    dir_names = ["1", "2", "3" ]
    doc_id = 1
    doc = ""
    for dirs in dir_names:
        for document in tqdm(listdir(folder + dirs)):
            with open (f"{folder + dirs}/{document}") as file:
                # print(f"{folder + dirs}/{document}")
                try:
                    doc = file.read()
                except:
                    print("file reading opsie")
                    continue
                tokens = pre_processing(doc)
                store_doc_info(dirs, doc_id, document, tokens)

            doc_id+=1



    # file_list = listdir("1")
    # file_name = file_list[136]
    # with open ("1/" + file_name) as doc:
    #     file = document_parser(doc.read())
    # doc.close()
    # tokens = token_time(segmenter.normalize_and_segment, file)#my_tokenizer(file)
    # print(tokens)
    # print(len(tokens))
    # print(e.logtime_data)

