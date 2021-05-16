from os import listdir
from tqdm import tqdm
from math import sqrt
from preprocessing import pre_processing, query_processor
from index import inverter, merge_index
from file_handeling import save_to_files, retrieve_posting_from_file, index_generator, queryfinder
from query import intersect

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
    for index, file_name in enumerate(documents_name):  # [:doc_id + limit - 1]):  #
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
    with open("Docinfo.txt", "w") as doc_info:
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


def save_inverted_index(invt_ind, index):
    with open(f"index_{index}_terms.txt", "w") as index_file:
        with open(f"index_{index}_posting.txt", "w") as posting_file:
            bytes_written = 0
            for key in invt_ind.keys():
                bytes_written += save_to_files(key, invt_ind[key], index_file, posting_file, bytes_written)
        posting_file.close()
    index_file.close()


# handles only single similar terms for now


def merge_all_indexs(dirs):
    indexs = []
    postings = []
    index_generators = []
    for directory in dirs:
        index = open(f"index_{directory}_terms.txt")
        posting = open(f"index_{directory}_posting.txt")
        ind_genrator = index_generator(index)
        index_generators.append(ind_genrator)
        indexs.append(index)
        postings.append(posting)

    terms = [next(ind) for ind in index_generators]
    merged_terms = open("inverted_index_terms.txt", "w")
    merged_postings = open("inverted_index_posting.txt", "w")
    bytes_written = 0
    counter = 0
    while terms:
        for i, term in enumerate(terms):
            if term is None:
                terms.remove(term)
                indexs.pop(i)
                postings.pop(i)
                index_generators.pop(i)

        if terms:
            min_pos = terms.index(min(terms))
            next_list = [min_pos]

            merged = merge_index({}, {terms[min_pos][0]: retrieve_posting_from_file(postings[min_pos], terms[min_pos][1])})
            for i in range(len(terms)):
                if i != min_pos:
                    if terms[i] == terms[min_pos]:
                        merged = merge_index(merged,
                                             {terms[min_pos][0]: retrieve_posting_from_file(postings[i], terms[i][1])})
                        next_list.append(i)

            bytes_written += save_to_files(terms[min_pos][0], merged[terms[min_pos][0]], merged_terms, merged_postings,
                                           bytes_written)

            for i in next_list:
                terms[i] = next(index_generators[i])
                counter += 1

        print(f"{counter} terms processed")


def load_documents(docs_file):
    docs_info = {}
    with open(docs_file) as docfile:
        while (info := docfile.readline()) != '':
            id, name, *extra = info.split(',')
            docs_info[id] = name
    return docs_info

def page_rank(queries):
    queries = query_processor(queries, "stoplist.txt")
    with open("inverted_index_terms.txt") as index:
        locations, not_found = queryfinder(queries, index)
    index.close()

    if not_found:
        print("following queriers were not found in the index ", end="     ")
        for left_out in not_found:
            print(left_out, end="   ")
        print()

    with open("inverted_index_posting.txt") as posting:
        posting_dict = retrieve_posting_from_file(posting, locations[0])
        docs = list(posting_dict.keys())
        docs.pop(0)  # removing the df key from the list of docs

        for location in locations[1:]:
            new_posting_dict = retrieve_posting_from_file(posting, location)
            new_docs = list(new_posting_dict.keys())
            new_docs.pop(0)
            docs.extend(new_docs)
    posting.close()
    return list(set(docs))


if __name__ == "__main__":
    doc_id = 1
    dirs = [] # ["1", "2", "3"] to directly get to quering
    while (directory := input("Enter Directory and -1 to stop  ")) != "-1":
        dirs.append(directory)
        invt_ind, doc_id = create_inverted_index(directory, doc_id, 10, "stoplist.txt")
        save_inverted_index(invt_ind, directory)

    if input("Do you want to merge all ? y to do it ") == "y":
        merge_all_indexs(dirs)

    queries = []
    while (query := input("Enter query term and -1 to stop ")) != "-1":
        queries.append(query)

    doc_info = load_documents("Docinfo.txt")
    results = page_rank(queries)
    results.sort()

    if results:
        print("The query terms were found in the following document")
        for result in results:
            print(doc_info[str(result)])
    else:
        print("No result found")
