#!/usr/bin/python

import fileinput
import json
import sys
from collections import OrderedDict

MIN_STRING_LENGTH = 6
TRAILING_ELLIPSES = "..."
MIN_CHAR_LENGTH = 3
ERROR_STRING = "<ERROR>"


def size(string):
    return len(string.encode('utf-8'))


class json_meta_data(object):
    def __init__(self, json_str):
        self.json_str = json_str
        self.json_obj = None
        self.json_str_size = None
        self.truncated_json_str_size = None
        self.str_values_size = None
        self.str_map = None

    def get_json_str(self):
        return self.json_str

    def set_truncated_json_str_size(self, truncated_json_str_size):
        self.truncated_json_str_size = truncated_json_str_size

    def get_truncated_json_str_size(self):
        if not self.truncated_json_str_size:
            self.truncated_json_str_size = size(self.json_str)
        return self.truncated_json_str_size

    def get_json_obj(self):
        if not self.json_obj:
            try:
                self.json_obj = json.loads(self.json_str)
            except Exception as e:
                print "incorrrect json format or some input error " + e.message
        return self.json_obj

    def set_json_obj(self, json_obj):
        self.json_obj = json_obj

    def get_json_str_size(self):
        if not self.json_str_size:
            self.json_str_size = size(self.json_str)
        return self.json_str_size

    def get_str_values_size(self):
        if not self.str_values_size:
            self.parse()
        return self.str_values_size

    def get_str_map(self):
        if not self.str_map:
            self.parse()
        return self.str_map

    # Max truncated object size
    def get_max_truncated_str_size(self):
        string_item_count = len(self.get_str_map())
        return (self.get_json_str_size() - self.get_str_values_size()) + (MIN_STRING_LENGTH * string_item_count)

    def update(self, string, truncated_str):
        str_map = self.get_str_map()
        return_ptr, key = str_map[string]
        if return_ptr:
            return_ptr[key] = truncated_str
        else:
            self.set_json_obj(truncated_str)
        del str_map[string]
        str_map[truncated_str] = return_ptr, key
        self.set_truncated_json_str_size(self.get_truncated_json_str_size() - size(string) + size(truncated_str))

    # Parsing the json_object by doing a exploratory analysis of the json obj
    def parse(self):
        stack = list()
        str_map = OrderedDict()
        stack.append((self.get_json_obj(), None, None))
        str_values_size = 0
        while stack:
            first_obj, return_ptr, key = stack.pop()
            if isinstance(first_obj, unicode) or isinstance(first_obj, str):
                str_map[first_obj] = return_ptr, key
                str_values_size += size(first_obj)
            if isinstance(first_obj, list):
                for key, ele in enumerate(first_obj):
                    stack.append((ele, first_obj, key))
            if isinstance(first_obj, dict):
                for key, ele in first_obj.iteritems():
                    stack.append((ele, first_obj, key))
        self.str_values_size, self.str_map = str_values_size, str_map


def main(max_bytes, filename):
    for line in fileinput.input(filename):
        process_line(line, max_bytes)


def process_line(line, max_bytes):
    json_meta_data_obj = json_meta_data(line)
    if truncate(json_meta_data_obj, max_bytes) != ERROR_STRING:
        print json.dumps(json_meta_data_obj.get_json_obj())
    else:
        print ERROR_STRING


def perform_word_boundary_compression(json_meta_data_obj, string, max_bytes):
    word_list = string.split()
    if len(word_list) > 2:
        truncated_str = word_list[0] + TRAILING_ELLIPSES + word_list[-1]
        truncated_str_size = json_meta_data_obj.get_json_str_size - size(string) + size(truncated_str)
        # trying to truncate a small part of the string instead of completely truncating the string
        if truncated_str_size < max_bytes:
            pass
    if size(truncated_str) < size(string):
        json_meta_data_obj.update(string, truncated_str)


def perform_trim_space_compression(json_meta_data_obj, string, max_bytes):
    truncated_str = string.strip()
    if size(truncated_str) < size(string):
        json_meta_data_obj.update(string, truncated_str)


def perform_basic_compression(json_meta_data_obj, string, max_bytes):
    truncated_str = string[:MIN_CHAR_LENGTH] + TRAILING_ELLIPSES
    truncated_str_size = json_meta_data_obj.get_truncated_json_str_size() - size(string) + size(truncated_str)
    if truncated_str_size < max_bytes:
        correction = max_bytes - truncated_str_size
        truncated_str = string[:(correction+MIN_CHAR_LENGTH)] + TRAILING_ELLIPSES
    if size(truncated_str) < size(string):
        json_meta_data_obj.update(string, truncated_str)


def truncate(json_meta_data_obj, max_bytes):
    # quick failure by finding out if you can truncate the string or not
    if json_meta_data_obj.get_max_truncated_str_size() > max_bytes:
        return ERROR_STRING
    if json_meta_data_obj.get_json_str_size() > max_bytes:
        for apply_compression in [perform_trim_space_compression,
                                  perform_basic_compression]:
            for string in json_meta_data_obj.get_str_map().keys():
                if json_meta_data_obj.get_truncated_json_str_size() > max_bytes:
                    apply_compression(json_meta_data_obj, string, max_bytes)
                else:
                    break
    return json_meta_data_obj


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: %s BYTES FILENAME' % sys.argv[0]
        sys.exit(1)

    main(int(sys.argv[1]), sys.argv[2])