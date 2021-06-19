from commandlines import Command
from preprocessing import query_processor, my_tokenizer, populate_stoplist
from file_handeling import queryfinder, retrieve_posting_from_file
from collections import namedtuple
from math import log, sqrt


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
        idf.append(log((n) / (term['df'])))
    return idf


def extract_term_info(query):
    queries = query_processor(query, "stoplist.txt")

    with open("inverted_index_terms.txt") as index:
        locations, not_found = queryfinder(queries, index)
    index.close()
    # queries = list(set(queries).difference(set(not_found)))
    with open("inverted_index_posting.txt") as posting:
        term_info = [retrieve_posting_from_file(posting, location) for location in locations]
    posting.close()

    return term_info


def calc_mag(query_infos):
    query_freqs = [query_info["tf"] for query_info in query_infos.values()]
    sum_squares = sum(tf * tf for tf in query_freqs)
    query_mag = sqrt(sum_squares)

    return query_mag


def vector_score(term_info, doc_info, query_info):
    scores = {}
    query_mag = calc_mag(query_info)
    inverse_df = idf(term_info, len(doc_info))
    for index, term in enumerate(term_info):
        keys = list(term.keys())
        for key in keys[1:]:
            if scores.get(key, False):
                scores[key] += term[key]['tf'] * inverse_df[index]
            else:
                scores[key] = term[key]['tf'] * inverse_df[index]

    for key in scores.keys():
        a = scores[key]
        scores[key] /= (float(doc_info[key].magnitude) * query_mag)

    scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
    return scores


def C_t(terms, n):
    ct = []
    for term in terms:
        ct.append(log((n - term['df'] + 0.5) / (0.5 + term['df'])))
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
    scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
    return scores

def query_score(score, the_query):
    term_info = extract_term_info(the_query)

    doc_info, L_davg = load_docinfo("Docinfo.txt")

    if score == 'okapi-TF':
        scores = okapi_tF(term_info, doc_info, L_davg)  # ,query_info)
    elif score == 'vector-space':
        query_info = my_tokenizer(the_query, populate_stoplist('stoplist.txt'))
        scores = vector_score(term_info, doc_info, query_info)

    # print(scores)
    # print(len(scores.keys()))
    #print(the_query)
    for i, key in enumerate(scores.keys()):
        yield f"{doc_info[key].path} {i + 1}  {scores[key]}"

if __name__ == "__main__":
    c = Command()

    default_options = {
        'score': 'okapi-TF',
        'q': 'Computer Science'
    }
    c.set_defaults(default_options)

    if c.contains_definitions('score'):
        score = c.get_definition('score')
    else:
        score = c.get_default('score')

    if c.contains_definitions('q'):
        the_query = c.get_definition('q')
    else:
        the_query = c.get_default('q')
    term_info = extract_term_info(the_query)

    doc_info, L_davg = load_docinfo("Docinfo.txt")
    if score == 'okapi-TF':

        scores = okapi_tF(term_info, doc_info, L_davg)  # ,query_info)
    elif score == 'vector-space':
        query_info = my_tokenizer(the_query, populate_stoplist('stoplist.txt'))
        scores = vector_score(term_info, doc_info, query_info)

    # print(scores)
    # print(len(scores.keys()))
    #print(the_query)
    for i, key in enumerate(scores.keys()):
        print(f"{doc_info[key].path} {i + 1}  {scores[key]}")
