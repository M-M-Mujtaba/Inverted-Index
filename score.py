from preprocessing import query_processor
from file_handeling import queryfinder, retrieve_posting_from_file
from collections import namedtuple
import math


def load_docinfo(docinfo_file):
    doc_info = namedtuple('Doc_Info', ['path', 'len', 'magnitude'])
    doc_info_dict = {}
    total_length = 0
    with open("Docinfo.txt") as docs:
        while (info := docs.readline()) != '':
            info = info[:-1].split(',')
            doc_info_dict[int(info[0])] = doc_info(*info[1:])
            total_length += int(info[2])

    return doc_info_dict, total_length / len(doc_info_dict)


def idf(terms, n):
    idf = []
    for term in terms:
        idf.append(math.log((1 + n) / (1 + term['df'])) + 1)
    return idf


def extract_term_info(query):
    queries = query_processor(query, "stoplist.txt")

    with open("inverted_index_terms.txt") as index:
        locations, not_found = queryfinder(queries, index)
    index.close()
    # queries = list(set(queries).difference(set(not_found)))
    print(queries)
    with open("inverted_index_posting.txt") as posting:
        term_info = [retrieve_posting_from_file(posting, location) for location in locations]
    posting.close()

    return term_info


def vector_score(term_info, doc_info):
    scores = {}

    inverse_df = idf(term_info, len(doc_info))
    for index, term in enumerate(term_info):
        keys = list(term.keys())
        for key in keys[1:]:
            if scores.get(key, False):
                scores[key] += term[key]['tf'] * inverse_df[index]
            else:
                scores[key] = term[key]['tf'] * inverse_df[index]

    scores = dict(sorted(scores.items()))
    for key in scores.keys():
        scores[key] /= int(doc_info[key].len)
    return scores


def C_t(terms, n):
    ct = []
    for term in terms:
        ct.append(math.log((n - term['df'] + 0.5) / (0.5 + term['df'])))
    return ct


def okapi_tF(term_info, doc_info, L_davg):
    scores = {}
    k1 = 1
    b = 1.5
    c_t = C_t(term_info, len(doc_info))
    for index, term in enumerate(term_info):
        keys = list(term.keys())
        for key in keys[1:]:
            if scores.get(key, False):
                scores[key] += ((k1 + 1) * term[key]['tf']) / (
                            k1 * ((1 - b) + b * (int(doc_info[key].len) / L_davg)) + term[key]['tf']) * c_t[index]
            else:
                scores[key] = ((k1 + 1) * term[key]['tf']) / (
                            k1 * ((1 - b) + b * (int(doc_info[key].len) / L_davg)) + term[key]['tf']) * c_t[index]
    return scores

if __name__ == "__main__":
    doc_info, L_davg = load_docinfo("Docinfo.txt")
    the_query = input("Enter your query")
    term_info = extract_term_info(the_query)
    scores = okapi_tF(term_info, doc_info, L_davg)
    print(scores)
