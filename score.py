from preprocessing import query_processor
from file_handeling import queryfinder, retrieve_posting_from_file
from collections import namedtuple
import math


def load_docinfo(docinfo_file):
    doc_info = namedtuple('Doc_Info', [ 'path', 'len', 'magnitude'])
    doc_info_dict = {}
    with open("Docinfo.txt") as docs:
        while (info := docs.readline()) != '':
            info = info[:-1].split(',')
            doc_info_dict[int(info[0])] = doc_info(*info[1:])

    return doc_info_dict
def idf(terms, n):
    idf = []
    for term in terms:
        idf.append(math.log((1 + n) / (1 + term['df']) ) + 1 )
    return idf


def vector_score(query, doc_info):

    scores = {}

    queries = query_processor(query, "stoplist.txt")

    with open("inverted_index_terms.txt") as index:
        locations, not_found = queryfinder(queries, index)
    index.close()
    #queries = list(set(queries).difference(set(not_found)))
    print(queries)
    with open("inverted_index_posting.txt") as posting:
        term_info = [retrieve_posting_from_file(posting, location) for location in locations]
    posting.close()

    inverse_df = idf(term_info, len(doc_info))
    for index, term in enumerate(term_info):
        keys = list(term.keys())
        for key in keys[1:]:
            if scores.get(key, False):
                scores[key] += term[key]['tf'] * inverse_df[index]
            else:
                scores[key] = term[key]['tf'] * inverse_df[index]

    scores = dict(sorted(scores.values()))
    return scores


if __name__ == "__main__":

    doc_info = load_docinfo("Docinfo.txt")
    the_query = input("Enter your query")
    scores = vector_score(the_query, doc_info)
    print(scores)