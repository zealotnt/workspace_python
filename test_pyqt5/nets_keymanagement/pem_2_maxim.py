#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import utils

import array
import sys
import key_management
sys.path.insert(0, '../../test_bluefinserial/bluefinserial')
from utils import *

if len(sys.argv) != 2:
	print("Error, usage:")
	print("%s <pri-pem-file>" % sys.argv[0])
	sys.exit(-1)

outputTemp = "/tmp/some_misc_file"


if key_management.checkPriKeyEncrypted(sys.argv[1]) == True:
	keyPass = input()
	# TODO: use temp lib instead
	key_management.genRawMaximKey(sys.argv[1], keyPass, outputTemp)
else:
	key_management.genRawMaximKey(sys.argv[1], "", outputTemp)

with open(outputTemp, "r") as f:
	key_vals = f.read()
	print(key_vals)
	f.close()
