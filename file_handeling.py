
def save_index_to_file(inverted_index, index_file, posting_file):
    index = {}
    bytes_written = 0
    with open(posting_file, "wb") as post_file:
        for key in inverted_index.keys():
            index[key] = {'start': bytes_written, 'end': 0}
            bytes_written += post_file.write(json.dumps(inverted_index[key]).encode('utf-8'))
            index[key]['end'] = bytes_written

    post_file.close()

    with open(index_file, "w") as ind_file:
        json.dump(index, ind_file)
    ind_file.close()


def rebuild_index_from_file(index_file, posting_file):
    inverted_index = {}

    with open(index_file) as ind_file:
        index = json.load(ind_file)
    ind_file.close()

    with open(posting_file, "rb") as post_file:
        for key in index.keys():
            post_file.seek(index[key]['start'])
            posting_byte = post_file.read(index[key]['end'] - index[key]['start'])
            posting = json.loads(posting_byte)
            inverted_index[key] = posting
    post_file.close()
    return inverted_index
