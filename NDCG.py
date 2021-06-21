from functools import reduce

from commandlines import Command
from math import log2
from operator import truediv
from json import dump



def doc_dict(corpus, sort):
    score_dict = {}
    while (query_rank := corpus.readline()) != '':
        query_rank = query_rank[:-1]
        query_rank = query_rank.split()

        if score_dict.get(query_rank[0], False):
            score_dict[query_rank[0]][query_rank[2]] = int(query_rank[3])
        else:
            score_dict[query_rank[0]] = {}
            score_dict[query_rank[0]][query_rank[2]] = int(query_rank[3])

    if sort:
        for key in score_dict.keys():
            score_dict[key] = dict(sorted(score_dict[key].items(), key=lambda item: item[1], reverse=True))

    return score_dict


def discounted_gains(scores, p):
    dsc_gain = []
    for i in range(1, p + 1):
        if i > 1:
            dsc_gain.append(scores[i - 1] / log2(i))
        else:
            dsc_gain.append(scores[i - 1])
    return dsc_gain

def combined_sum(num):
    sum = 0
    while True:
        sum += num
        num = yield sum

def accummulate_gains(dsc_gains) :
    sum = combined_sum(0)
    next(sum)
    DCGp = [sum.send(dsc_gain) for dsc_gain in dsc_gains]
    return DCGp

def get_scores(document_positions, base_rank_dict, p):
    score_dict = {}
    for query in document_positions.keys():
        score_dict[query] = {}
        for docs, document in enumerate(document_positions[query].keys()):
            if docs < p:
                if (score := base_rank_dict[query].get(document, -3)) > -3:
                    score_dict[query][document] = score
                else:
                    score_dict[query][document] = 0

            else:
                break
    return score_dict

def calc_NDCG(test_score, base_score):
    NDCG = {}

    for query in base_score.keys():

        NDCG[query] = list(map(truediv, test_score[query], base_score[query]))
    return NDCG

def run_NDGG_for_report(p, my_file):
    base_score_file = "corpus.qrel"
    my_score_file = my_file

    with open(base_score_file) as corpus:
        base_rank_dict = doc_dict(corpus, True)
    corpus.close()

    IDCGp = {}
    for key in base_rank_dict.keys():
        base_discounted_gain = discounted_gains(list(base_rank_dict[key].values()), p)
        IDCGp[key] = accummulate_gains(base_discounted_gain)

    with open(my_score_file) as my_score:
        document_positions = doc_dict(my_score, False)

    my_rank_dict = get_scores(document_positions, base_rank_dict, p)
    DCGp = {}

    for key in my_rank_dict.keys():
        my_discounted_gains = discounted_gains(list(my_rank_dict[key].values()), p)
        DCGp[key] = accummulate_gains(my_discounted_gains)

    # for key in DCGp.keys():
    #     print(DCGp[key])

    NDCG = calc_NDCG(DCGp, IDCGp)

    return NDCG
def p_score(scores_lists):
    last_scores = [score_list[-1] for score_list in scores_lists]
    return last_scores

if __name__ == "__main__":

    report_data = {}
    for p in range(1, 15 + 1):
        report_data[p] = {}
        okapi_NDCG = run_NDGG_for_report(p, "okapi-TF.txt")
        vector_space_NDCG = run_NDGG_for_report(p, "vector-space.txt")
        query_keys = list(okapi_NDCG.keys())
        okapi_scores = p_score(list(okapi_NDCG.values()))
        vector_space_score = p_score(list(vector_space_NDCG.values()))

        report_data[p]["Okapi TF"] = dict(zip(query_keys, okapi_scores))
        report_data[p]["Okapi TF"]["Average NDCG"] = reduce(lambda a, b: a + b, okapi_scores) / len(okapi_scores)
        report_data[p]["Vector Space"] = dict(zip(query_keys, vector_space_score))
        report_data[p]["Vector Space"]["Average NDCG"] = reduce(lambda a, b: a + b, vector_space_score) / len(vector_space_score)

    with open("report_data.json", "w") as data_file:
        dump(report_data, data_file , indent=2)








    # c = Command()
    #
    # default_options = {
    #     'p': 3
    # }
    #
    # c.set_defaults(default_options)
    #
    # if c.contains_definitions('p'):
    #     p = int(c.get_definition('p'))
    # else:
    #     p = c.get_default('p')
    #
    #
    # base_score_file = c.arg0
    # my_score_file = c.arg1
    #
    # with open(base_score_file) as corpus:
    #     base_rank_dict = doc_dict(corpus, True)
    # corpus.close()
    #
    # IDCGp = {}
    # for key in base_rank_dict.keys():
    #     base_discounted_gain = discounted_gains(list(base_rank_dict[key].values()), p)
    #     IDCGp[key] = accummulate_gains(base_discounted_gain)
    #
    # with open(my_score_file) as my_score:
    #     document_positions = doc_dict(my_score, False)
    #
    #
    # my_rank_dict = get_scores(document_positions, base_rank_dict, p)
    # DCGp = {}
    #
    # for key in my_rank_dict.keys():
    #     my_discounted_gains = discounted_gains(list(my_rank_dict[key].values()), p)
    #     DCGp[key] = accummulate_gains(my_discounted_gains)
    #
    # # for key in DCGp.keys():
    # #     print(DCGp[key])
    #
    # NDCG = calc_NDCG(DCGp, IDCGp)
    #
    # for key in NDCG.keys():
    #     print(f"for query {key} NDGC scores are {NDCG[key]}")