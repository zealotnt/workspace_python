__author__ = 'zealotnt'

import sys
import os
import binascii

VERBOSE = 0
EXTRA_VERBOSE = 0

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_err(text):
    print >> sys.stderr, bcolors.FAIL + text + bcolors.ENDC


def print_ok(text):
    print bcolors.OKGREEN + text + bcolors.ENDC


def get_fullpath(file_dir, file_name):
    if file_dir == "":
        return file_name
    if os.name == "posix":
        return file_dir + '/' + file_name
    if os.name == "nt":
        return file_dir + '\\' + file_name

def dump_hex(data, desc_str = ""):
    print desc_str + binascii.hexlify(data)
