#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-09 11:24:38

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives.asymmetric import utils

import sys
import git
import os
import inspect
def get_git_root():
	CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep
	path = CURRENT_DIR
	git_repo = git.Repo(path, search_parent_directories=True)
	git_root = git_repo.git.rev_parse("--show-toplevel")
	print (git_root)
	return git_root
sys.path.insert(0, get_git_root() + '/test_bluefinserial/bluefinserial')
from utils import *

def main():
	private_key = dsa.generate_private_key(
		key_size=1024,
		backend=default_backend()
	)

	# Parameters and Keys dumping
	# p: public modulus
	print("p: ", private_key.public_key().public_numbers().parameter_numbers.p)
	# q: sub-group order
	print("q: ", private_key.public_key().public_numbers().parameter_numbers.q)
	# g: generator
	print("g: ", private_key.public_key().public_numbers().parameter_numbers.g)
	# y: public value
	print("y: ", private_key.public_key().public_numbers().y)
	# x: private value
	print("x: ", private_key.private_numbers().x)

	# Sign
	data = b"this is some data I'd like to sign"
	signature = private_key.sign(
		data,
		hashes.SHA256()
	)
	print("signature: ", signature)

	# Verify
	public_key = private_key.public_key()
	print("Verify: ", public_key.verify(
			signature,
			data,
			hashes.SHA256()
		)
	)
	r_s = utils.decode_dss_signature(signature)
	sig_r = r_s[0]
	sig_s = r_s[1]

	# Dump hex value
	print("\r\nHex value")
	dump_hex(
		packl_ctypes(private_key.public_key().public_numbers().parameter_numbers.p),
		'p',
		preFormat="C"
	)
	dump_hex(
		packl_ctypes(private_key.public_key().public_numbers().parameter_numbers.q),
		'q',
		preFormat="C"
	)
	dump_hex(
		packl_ctypes(private_key.public_key().public_numbers().parameter_numbers.g),
		'g',
		preFormat="C"
	)
	dump_hex(
		packl_ctypes(private_key.public_key().public_numbers().y),
		'y',
		preFormat="C"
	)
	dump_hex(
		packl_ctypes(private_key.private_numbers().x),
		'x',
		preFormat="C"
	)
	dump_hex(
		data,
		'data',
		preFormat="C"
	)
	dump_hex(
		signature,
		'signature',
		preFormat="C"
	)
	dump_hex(
		packl_ctypes(sig_r),
		'signature_r',
		preFormat="C"
	)
	dump_hex(
		packl_ctypes(sig_s),
		'signature_s',
		preFormat="C"
	)

if __name__ == "__main__":
	main()
