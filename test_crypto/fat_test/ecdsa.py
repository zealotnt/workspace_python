#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-09 15:12:53


# To import utility of repo
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

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import utils

def main():
	# Key generation
	private_key = ec.generate_private_key(
		ec.SECP256K1(), default_backend()
	)
	public_key = private_key.public_key()

	# Keys dumping
	print("pub_x: ", public_key.public_numbers().x)
	print("pub_y: ", public_key.public_numbers().y)
	print("pri:   ", private_key.private_numbers().private_value)

	# Sign
	data = b"this is some data I'd like to sign"
	signature = private_key.sign(
		data,
		ec.ECDSA(hashes.SHA256())
	)
	print("signature", signature)
	r_s = utils.decode_dss_signature(signature)
	sig_r = r_s[0]
	sig_s = r_s[1]

	# Verify
	print("verify", public_key.verify(signature, data, ec.ECDSA(hashes.SHA256())))


	# Dump hex value
	print("\r\nHex value")
	dump_hex(
		packl_ctypes(public_key.public_numbers().x),
		'x',
		preFormat="C"
	)
	dump_hex(
		packl_ctypes(public_key.public_numbers().y),
		'y',
		preFormat="C"
	)
	dump_hex(
		packl_ctypes(private_key.private_numbers().private_value),
		'pri',
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
