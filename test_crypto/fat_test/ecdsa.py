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
	dumpFileText = ""
	filePathSave = ""
	keyLength = 256
	if len(sys.argv) == 2:
		filePathSave = ProcessFilePath(sys.argv[1])

	# Key generation
	private_key = ec.generate_private_key(
		ec.SECP256R1(), default_backend()
	)
	public_key = private_key.public_key()

	# Keys dumping
	print("pub_x: ", public_key.public_numbers().x)
	print("pub_y: ", public_key.public_numbers().y)
	print("pri:   ", private_key.private_numbers().private_value)

	# Sign
	data = os.urandom(keyLength)
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
	to_Dump = [[
		FixedBytes(keyLength/8, packl_ctypes(public_key.public_numbers().x)),
		'ecdsa_x_',
	],[
		FixedBytes(keyLength/8, packl_ctypes(public_key.public_numbers().y)),
		'ecdsa_y_',
	],[
		FixedBytes(keyLength/8, packl_ctypes(private_key.private_numbers().private_value)),
		'ecdsa_pri_',
	],[
		data,
		'ecdsa_data_',
	],[
		FixedBytes(keyLength/8, packl_ctypes(sig_r)),
		'ecdsa_signature_r_',
	],[
		FixedBytes(keyLength/8, packl_ctypes(sig_s)),
		'ecdsa_signature_s_',
	]]
	for idx, item in enumerate(to_Dump):
		dumpFileText += dump_hex(
			item[0],
			item[1],
			preFormat="C"
		)

	if filePathSave != "":
		dumpFileText = "#include <stdint.h>\r\n\r\n" + dumpFileText
		f = open(filePathSave, "w")
		f.write(dumpFileText)
		f.close()
		print_ok("Dump buffer data to " + filePathSave)

if __name__ == "__main__":
	main()
