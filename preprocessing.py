import re
from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer

# from nltk.wordnet import WordNetLemmatizer


my_re = re.compile("[a-zA-Z]+-{0,1}'{0,1}[a-zA-z]+")
stemmer = SnowballStemmer(language='english')

"""
This function populates the stop list used for discarding unwanted tokens
Input: name of the file that stores top words in the format word(linebreak)word(linebreak)....EOF
Output: a dict with stop words as key and bool value true
e.g
{"he": True, "the": True}

"""


def populate_stoplist(file_name: str):
    try:
        with open(file_name) as stoplist_file:
            words = stoplist_file.read()
    except:
        print("Incorrect stoplist file path")
        exit(-1)
    stop_list = {word: True for word in words.split("\n")}

    return stop_list


"""
This function parse the html page(provided as string) using beautiful soup
and return it's body contents
Input: Html document as string
Output: document body text without any tags

"""


def document_parser(document: str):
    soup = BeautifulSoup(document)
    body = soup.body
    if body is None:
        return None
    parsed_document = body.get_text()

    return parsed_document


def query_processor(queires, stop_file):
    stop_list = populate_stoplist(stop_file)
    queires = [stemmer.stem(query.lower()) if not stop_list.get(query, False) else "" for query in queires]
    while "" in queires:
        queires.remove("")
    return queires


"""
This is the tokenization function it transforms the input text string into set of tokens
with each token it's position and over document frequency is also provided
Input: parsed document as string and stop_list(of strings) of words to be discarded for tokens
Output: Tokens dictionary: format {Token: { "positions" : [], "tf"}}
e.g
{"hello": {"positions": [ 2, 5, 8], "tf":3 }, "ballo": {"positinos": [ 2, 5], "tf": 2}}
"""


def my_tokenizer(document: str, stop_list: list):
    token_positioning = {}

    for index, token in enumerate(my_re.findall(document)):
        text = token.lower()

        if not stop_list.get(text, False):  # if the token is not found in stop list then

            text = stemmer.stem(text)

            if token_positioning.get(text, False):  # if the token exists in the dict before
                token_positioning[text]["positions"].append(index)
                token_positioning[text]["tf"] += 1
            else:
                token_positioning[text] = {"positions": [index], "tf": 1}  # create new token entry

    return token_positioning


"""
This is the main function of this file.
it gets a list of documents and return a list of tokens which includes tokens for each document
Input: documents list [<html><p>" Hello this is a doc</p>,</html>", .........]
stop_file: file name for the file which contains all the stop words to be used in this index creation
Output: Generator object which yield's token for each document (list of tokens)

"""


def pre_processing(documents: list, stop_file):
    stop_list = populate_stoplist(stop_file)
    for document in documents:
        document = document_parser(document)
        if document is None:
            yield None
            continue
        tokens = my_tokenizer(document, stop_list)
        yield tokens
