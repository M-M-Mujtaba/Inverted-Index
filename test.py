test_dict = {'a-ha': {'df': 2, 4: {'positions': [623, 632], 'tf': 2}, 5: {'positions': [623, 632], 'tf': 2}},
             'a-sweet': {'df': 2, 8: { 'positions': [24], 'tf': 1}, 9: {'positions': [24], 'tf': 1}},
             'heart-healthi': {'df': 2,  8: {'positions': [246], 'tf': 1}, 9: {'positions': [246], 'tf': 1}}}
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
        prev = input
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
        delta_position.send(0)
        index += terms
    return posting_dict


#print(posting_dict_to_list(test_dict['a-ha']))

def save_to_files(token: str, posting_dict: dict, index, posting, byte_location):

    posting_list = posting_dict_to_list(posting_dict)
    for val in posting_list:
        posting.write(val.to_bytes(length= 2, byteorder= 'big'))
    ending = (len(posting_list) * 2 )+ byte_location
    index.write(f"{token}, {byte_location}, {ending}\n")
    return ending


def retrieve_from_file(posting, byte_location, ending):
    posting_list = []
    posting.seek(byte_location)
    for i in range(((ending - byte_location) // 2)):
        posting_list.append(int.from_bytes(posting.read(2), byteorder='big'))
    return posting_list_to_dict(posting_list)

with open("index.txt", "w") as index:
    with open("posting.bin", "wb") as posting:
        bytes_sofar = 0
        for key in test_dict.keys():
            bytes_sofar = save_to_files(key, test_dict[key], index, posting, bytes_sofar)
            print(bytes_sofar)
        posting.close()
    index.close()

# with open("posting.bin", "rb") as posting:
#     print(retrieve_from_file(posting, 18, 32))

""""
working code above this poitn 
"""
# with open("test.bin", "wb") as test:
#     for key in test_dict.keys():
#         index[key] = bytes_writen
#         bytes_writen += test.write(test_dict[key]["df"].to_bytes(length =2, byteorder='big'))
#         docs = list(test_dict[key].keys())
#         docs.pop(1)
#         prev_doc = 0
#         for doc in docs:
#             delta_doc = doc - prev_doc
#             bytes_writen += test.write(delta_doc.to_bytes(length =2, byteorder='big'))
#             bytes_writen += test.write(test_dict[key][doc]["tf"].to_bytes(length =2, byteorder='big'))
#
#             for position in test_dict[key][doc]["positions"]:
#
#                 bytes_writen += test.write(position.to_bytes(length =2, byteorder='big'))
#                 prev_pos = position
#             prev_doc = doc
#


# from struct import pack, unpack
#
#
# def encode_number(number):
#     """Variable byte code encode number.
#     Usage:
#       import vbcode
#       vbcode.encode_number(128)
#     """
#     bytes_list = []
#     while True:
#         bytes_list.insert(0, number % 128)
#         if number < 128:
#             break
#         number = number // 128
#     bytes_list[-1] += 128
#     return pack('%dB' % len(bytes_list), *bytes_list)
#
#
# def encode(numbers):
#     """Variable byte code encode numbers.
#     Usage:
#       import vbcode
#       vbcode.encode([32, 64, 128])
#     """
#     bytes_list = []
#     for number in numbers:
#         bytes_list.append(encode_number(number))
#     return b"".join(bytes_list)
#
#
# def decode(bytestream):
#     """Variable byte code decode.
#     Usage:
#       import vbcode
#       vbcode.decode(bytestream)
#         -> [32, 64, 128]
#     """
#     n = 0
#     numbers = []
#     bytestream = unpack('%dB' % len(bytestream), bytestream)
#     for byte in bytestream:
#         if byte < 128:
#             n = 128 * n + byte
#         else:
#             n = 128 * n + (byte - 128)
#             numbers.append(n)
#             n = 0
#     return numbers
# import sys as sys
# print(sys.getsizeof([2, 1200, 7, 25, 50, 100, 350, 500, 2000, 2250, 1201, 3, 34, 129, 256]))
# with open("test.bin", "wb") as test_file:
#     print(test_file.write(encode([2, 1200, 7, 25, 50, 100, 350, 500, 2000, 2250, 1201, 3, 34, 129, 256])))
#
# test_file.close()
