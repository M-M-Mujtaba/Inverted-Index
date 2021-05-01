import json
import sys

test_dict = {'a-ha': {4: {'positions': [623, 9], 'tf': 2}, 'df': 2, 5: {'positions': [623, 9], 'tf': 2}},
             'a-sweet': {8: {'positions': [24], 'tf': 1}, 'df': 2, 9: {'positions': [24], 'tf': 1}},
             'heart-healthi': {8: {'positions': [246], 'tf': 1}, 'df': 2, 9: {'positions': [246], 'tf': 1}}}
index = {}
# json.dumps(test_dict).encode('utf-8')

bytes_written = 0
with open("test.bin", "wb") as test_file:
    for key, values in test_dict.items():
        index[key] = {'start': bytes_written, 'end': 0}
        bytes_written += test_file.write(json.dumps(test_dict[key]).encode('utf-8'))
        index[key]['end'] = bytes_written

test_file.close()

posting_recover = {}
with open("test.bin", "rb") as test_file:

    test_file.seek(index['a-sweet']['start'])
    read_bytes = test_file.read(index['a-sweet']['end']-index['a-sweet']['start'])
    print(read_bytes)
    posting_recover = json.loads(read_bytes)
print(posting_recover)
