
with open("test.txt", "w") as test:
    print(test.write(str(259)))
    print(test.write(str(134324234)))

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
