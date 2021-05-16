index = {}
bytes_writen = 0


def difference(input):
    prev = 0
    while True:
        delta = input - prev
        prev = input
        input = yield delta


def inverse_difference(input):
    prev = 0
    while True:
        delta_dash = input + prev
        prev = delta_dash
        input = yield delta_dash


def posting_dict_to_list(the_dict):
    posting_list = [the_dict["df"]]
    delta = difference(0)
    next(delta)
    docs = list(the_dict.keys())
    # ignoring the df key
    posting_list.extend([delta.send(doc) for doc in docs[1:]])
    delta.send(0)
    inserted = 0
    for i in range(1, len(docs)):
        posting_list.insert(i + 1 + inserted, the_dict[docs[i]]["tf"])
        inserted += 1
        posting_list[i + 1 + inserted:i + 1 + inserted] = [delta.send(position) \
                                                           for position in the_dict[docs[i]]["positions"]]
        delta.send(0)
        inserted += len(the_dict[docs[i]]["positions"])
    return posting_list


def posting_list_to_dict(the_list):
    posting_dict = {}
    index = 0
    delta_doc = inverse_difference(0)
    next(delta_doc)
    delta_position = inverse_difference(0)
    next(delta_position)
    posting_dict["df"] = the_list[index]
    index += 1
    for i in range(posting_dict["df"]):
        doc_id = delta_doc.send(the_list[index])
        posting_dict[doc_id] = {}
        index += 1

        terms = the_list[index]
        posting_dict[doc_id]["tf"] = terms
        index += 1

        posting_dict[doc_id]["positions"] = [delta_position.send(position) \
                                             for position in the_list[index: index + terms]]
        delta_position.send(-delta_position.send(0))
        index += terms
    return posting_dict


# print(posting_dict_to_list(test_dict['a-ha']))

def save_to_files(token: str, posting_dict: dict, index, posting, byte_location: int):
    posting_list = posting_dict_to_list(posting_dict)
    bytes_written = 0
    for val in posting_list[:-1]:
        bytes_written += posting.write(str(val))
        bytes_written += posting.write(',')
    bytes_written += posting.write(str(posting_list[-1]))
    bytes_written += posting.write('\n')
    index.write(f"{token}, {byte_location}\n")
    return bytes_written + 1


def retrieve_posting_from_file(posting, byte_location):
    posting_list = []
    posting.seek(byte_location)
    posting_text = posting.readline()
    posting_list = [int(val) for val in posting_text[:-1].split(',')]
    return posting_list_to_dict(posting_list)


def index_generator(index):
    while (index_pos := index.readline()) != '':
        term, byte_postition = index_pos.split(',')
        yield term, int(byte_postition)
    yield None
