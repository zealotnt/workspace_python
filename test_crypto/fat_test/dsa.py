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
	dumpFileText = ""
	dumpStyle = "C"
	dumpStyleSupport = [ "C", "raw" ]
	filePathSave = ""
	SHA_FUNCS = [hashes.SHA1(), hashes.SHA256(), hashes.SHA256()]
	KEY_LENGTHS = [1024, 2048, 3072]
	DSA_MAX_SIG_LENS = [20, 32, 32]

	if len(sys.argv) == 2:
		filePathSave = ProcessFilePath(sys.argv[1])
	elif len(sys.argv) == 3:
		filePathSave = ProcessFilePath(sys.argv[1])
		dumpStyle = sys.argv[2]
		if dumpStyle not in dumpStyleSupport:
			print_err("Not support type %s" % (dumpStyle))
			sys.exit(-1)

	for idx, keyLength in enumerate(KEY_LENGTHS):
		private_key = dsa.generate_private_key(
			key_size=keyLength,
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
			SHA_FUNCS[idx]
		)

		# Verify
		public_key = private_key.public_key()
		print("Verify: ", public_key.verify(
				signature,
				data,
				SHA_FUNCS[idx]
			)
		)
		r_s = utils.decode_dss_signature(signature)
		sig_r = r_s[0]
		sig_s = r_s[1]
		r_s_str = (FixedBytes(DSA_MAX_SIG_LENS[idx], packl_ctypes(sig_r)) +
				   FixedBytes(DSA_MAX_SIG_LENS[idx], packl_ctypes(sig_s)))
		# r_s_str = packl_ctypes(sig_r) + packl_ctypes(sig_s)
		dump_hex(r_s_str, "signature: ")

		# Dump hex value
		print("\r\nHex value")
		toDump = [[
				TrimZeroes(packl_ctypes(private_key.public_key().public_numbers().parameter_numbers.p)),
				'dsa_p_' + str(keyLength)
			], [
				TrimZeroes(packl_ctypes(private_key.public_key().public_numbers().parameter_numbers.q)),
				'dsa_q_' + str(keyLength)
			], [
				TrimZeroes(packl_ctypes(private_key.public_key().public_numbers().parameter_numbers.g)),
				'dsa_g_' + str(keyLength)
			], [
				TrimZeroes(packl_ctypes(private_key.public_key().public_numbers().y)),
				'dsa_y_' + str(keyLength)
			], [
				TrimZeroes(packl_ctypes(private_key.private_numbers().x)),
				'dsa_x_' + str(keyLength)
			], [
				data,
				'dsa_data_' + str(keyLength)
			], [
				FixedBytes(DSA_MAX_SIG_LENS[idx]*2, r_s_str),
				'dsa_signature_' + str(keyLength),
			], [
				FixedBytes(DSA_MAX_SIG_LENS[idx], packl_ctypes(sig_r)),
				'dsa_signature_r_'+ str(keyLength),
			], [
				FixedBytes(DSA_MAX_SIG_LENS[idx], packl_ctypes(sig_s)),
				'dsa_signature_s_'+ str(keyLength),
			]
		]
		for idx, item in enumerate(toDump):
			dumpFileText += dump_hex(
				item[0],
				item[1],
				preFormat=dumpStyle
			)

	if filePathSave != "":
		dumpFileText = "#include <stdint.h>\r\n\r\n" + dumpFileText
		f = open(filePathSave, "w")
		f.write(dumpFileText)
		f.close()
		print_ok("Dump buffer data to " + filePathSave)

if __name__ == "__main__":
	main()
