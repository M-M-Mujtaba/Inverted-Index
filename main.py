from os import listdir
from tqdm import tqdm
from math import sqrt
from preprocessing import pre_processing
from index import inverter, merge_index

"""
This function implement's task 4
It stores directory/docid with it's length and it's magnitude
length is calculated by summing all token frequencies in a doc
magnitude is calculated by summing square of all frequencies in doc and then taking square root
"""


def store_doc_info(doc_info, directory: str, doc_id: int, doc_name: str, tokens: dict):
    tok_freqs = [token_info["tf"] for token_info in tokens.values()]
    sum_squares = sum(tf * tf for tf in tok_freqs)
    doc_len = sum(tok_freqs)
    doc_mag = sqrt(sum_squares)

    doc_info.write(f"{doc_id},{directory}/{doc_name},{doc_len},{doc_mag}\n")


"""
This is one of the core function that creates and saves inverted index for all the files in the directory


"""


def create_inverted_index(directory, doc_id, limit, stop_file):
    inverted_index = {}
    documents_name = listdir(directory)
    documents = []
    for index, file_name in enumerate(documents_name[:doc_id + limit - 1]):  #
        with open(f"{directory}/{file_name}") as file:
            try:
                doc = file.read()
            except:
                print(f"could not read file {documents_name[index]}")
                documents_name.pop(index)
                file.close()
                continue
            documents.append(doc)
            file.close()
    print(len(documents))
    with open("Docinfo.txt", "a") as doc_info:
        for index, tokens in tqdm(enumerate(pre_processing(documents, stop_file))):
            if tokens is not None:
                store_doc_info(doc_info, directory, doc_id, documents_name[index], tokens)
                inverted = inverter(tokens, doc_id)
                inverted_index = merge_index(inverted_index, inverted)
                doc_id += 1
            else:
                print(f"body not found for {documents_name[index]}")
                documents_name.pop(index)
                documents.pop(index)

    doc_info.close()
    return inverted_index, doc_id


if __name__ == "__main__":
    doc_id = 1
    invt_ind, doc_id = create_inverted_index("1", doc_id, 10, "stoplist.txt")
    print(invt_ind["amount"])
