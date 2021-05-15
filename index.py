"""
Converts all the tokens of single document into an inverted index format:
Makes doc_id a key to dictionary where positions and tf are stored and initializes df as 1
Input: tokens dictionary from preprocessing function and doc_id
e.g
{"hello": {"positions": [ 2, 5, 8], "tf":3 }, "ballo": {"positinos": [ 2, 5], "tf": 2}}, 3
output: inverted index
e.g
{"hello": {3: {"positions": [ 2, 5, 8], "tf":3 }, "df":1,}, "ballo": { 3:{"positinos": [ 2, 5], "tf": 2}}, "df":1}}
"""

def inverter(tokens: dict, doc_id: int):
    inverted_index = {}
    for key in tokens.keys():
        inverted_index[key] = {}
        inverted_index[key]["df"] = 1
        inverted_index[key][doc_id] = tokens[key]


    # sort the dictionary on token(the key)
    inverted_index = dict(sorted(inverted_index.items()))

    return inverted_index


"""
takes 2 inverted index to merge them and return them as one
For this case we merge invt_ind into inverted_index
E.g
Inverted_index = {'a-ha': {4: {'positions': [623, 9], 'tf': 2}, 'df': 2, 5: {'positions': [623, 9], 'tf': 2}},
                 'a-sweet': {8: {'positions': [24], 'tf': 1}, 'df': 2, 9: {'positions': [24], 'tf': 1}}}
invt_index =      {'heart-healthi': {8: {'positions': [246], 'tf': 1}, 'df': 2, 9: {'positions': [246], 'tf': 1}}}

output =          {'a-ha': {4: {'positions': [623, 9], 'tf': 2}, 'df': 2, 5: {'positions': [623, 9], 'tf': 2}},
                  'a-sweet': {8: {'positions': [24], 'tf': 1}, 'df': 2, 9: {'positions': [24], 'tf': 1}},
                  'heart-healthi': {8: {'positions': [246], 'tf': 1}, 'df': 2, 9: {'positions': [246], 'tf': 1}}}
"""


def merge_index(inverted_index: dict, invt_ind: dict):
    # this if is for the first initial case when we haven't created
    # the inverted index while starting to create inverted index
    if not inverted_index:
        return invt_ind
    else:
        for key in invt_ind.keys():

            # if the entry exists already in the inverted_index
            if inverted_index.get(key, False):


                for doc_id in invt_ind[key].keys():
                    if doc_id != 'df':
                        # if the token term of inverted_index has the same doc id
                        if inverted_index[key].get(doc_id, False):
                            # add terms into that doc_id dictionary
                            inverted_index[key][doc_id]["tf"] += invt_ind[key][doc_id]["tf"]
                            inverted_index[key][doc_id]["positions"].extend(invt_ind[key][doc_id]["positions"])

                        else:
                            # create a new doc_id key in inverted_index and place the contents
                            # of invt_ind doc_id into it and increment the document frequency
                            inverted_index[key][doc_id] = invt_ind[key][doc_id]
                            inverted_index[key]["df"] += 1
            else:
                # add the whole term and all its docs and positioning into inverted_index from invt_ind
                inverted_index[key] = invt_ind[key]
    # sort the dictionary on token(the key)
    # some new tokens would be out of place so we need to sort it again
    inverted_index = dict(sorted(inverted_index.items()))

    return inverted_index
