"""

Input: Iterators of both posting list to be intersected
Output: list of document which were present in both posting list
"""


def intersect(posting1: list, posting2: list):
    # common_documents = []
    # posting1_doc, _ = next(posting1)
    # posting2_doc, _ = next(posting2)
    # while posting1_doc is not None and posting2_doc is not None:
    #     if posting1_doc == posting2_doc:
    #         common_documents.append(posting1_doc)
    #     elif posting1_doc > posting2_doc:
    #         posting2_doc, _ = next(posting2)
    #     else:
    #         posting1_doc, _ = next(posting1)
    # return common_documents
    return list(set(posting1).intersection(set(posting2)))
