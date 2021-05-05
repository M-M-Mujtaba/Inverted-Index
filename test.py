# import json
# import sys
#
# test_dict = {'a-ha': {4: {'positions': [623, 9], 'tf': 2}, 'df': 2, 5: {'positions': [623, 9], 'tf': 2}},
#              'a-sweet': {8: {'positions': [24], 'tf': 1}, 'df': 2, 9: {'positions': [24], 'tf': 1}},
#              'heart-healthi': {8: {'positions': [246], 'tf': 1}, 'df': 2, 9: {'positions': [246], 'tf': 1}}}
# index = {}
# # json.dumps(test_dict).encode('utf-8')
#
# bytes_written = 0


from struct import pack, unpack


def encode_number(number):
    """Variable byte code encode number.
    Usage:
      import vbcode
      vbcode.encode_number(128)
    """
    bytes_list = []
    while True:
        bytes_list.insert(0, number % 128)
        if number < 128:
            break
        number = number // 128
    bytes_list[-1] += 128
    return pack('%dB' % len(bytes_list), *bytes_list)


def encode(numbers):
    """Variable byte code encode numbers.
    Usage:
      import vbcode
      vbcode.encode([32, 64, 128])
    """
    bytes_list = []
    for number in numbers:
        bytes_list.append(encode_number(number))
    return b"".join(bytes_list)


def decode(bytestream):
    """Variable byte code decode.
    Usage:
      import vbcode
      vbcode.decode(bytestream)
        -> [32, 64, 128]
    """
    n = 0
    numbers = []
    bytestream = unpack('%dB' % len(bytestream), bytestream)
    for byte in bytestream:
        if byte < 128:
            n = 128 * n + byte
        else:
            n = 128 * n + (byte - 128)
            numbers.append(n)
            n = 0
    return numbers
import sys as sys
print(sys.getsizeof([2, 1200, 7, 25, 50, 100, 350, 500, 2000, 2250, 1201, 3, 34, 129, 256]))
with open("test.bin", "wb") as test_file:
    print(test_file.write(encode([2, 1200, 7, 25, 50, 100, 350, 500, 2000, 2250, 1201, 3, 34, 129, 256])))

test_file.close()