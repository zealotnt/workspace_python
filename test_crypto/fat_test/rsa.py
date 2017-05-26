#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-09 09:44:43


# To import utility of repo
import sys
import git
import os
import struct
import inspect
def get_git_root():
	CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep
	path = CURRENT_DIR
	git_repo = git.Repo(path, search_parent_directories=True)
	git_root = git_repo.git.rev_parse("--show-toplevel")
	return git_root
sys.path.insert(0, get_git_root() + '/test_bluefinserial/bluefinserial')
from utils import *

# To generate random message
import random, string

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from Crypto.PublicKey import RSA

# [Source](http://stackoverflow.com/questions/2030053/random-strings-in-python)
def randomword(length):
	randomStr = ''.join(random.choice(string.lowercase) for i in range(length))
	print(len(randomStr))
	return randomStr

def main():
	dumpFileText = ""
	dumpStyle = "C"
	dumpStyleSupport = [ "C", "raw" ]
	filePathSave = ""
	KEY_LENGTHS = [512, 1024, 2048, 3072]
	if len(sys.argv) == 2:
		filePathSave = ProcessFilePath(sys.argv[1])
	elif len(sys.argv) == 3:
		filePathSave = ProcessFilePath(sys.argv[1])
		dumpStyle = sys.argv[2]
		if dumpStyle not in dumpStyleSupport:
			print_err("Not support type %s" % (dumpStyle))
			sys.exit(-1)

	for keyLength in KEY_LENGTHS:
		# Key generation
		private_key = rsa.generate_private_key(public_exponent=65537, key_size=keyLength, backend=default_backend())
		public_key = private_key.public_key()

		# Key dumping
		print("p*q ", private_key.private_numbers().p * private_key.private_numbers().q)
		print("n   ", private_key.private_numbers().public_numbers.n)
		print("e   ", private_key.private_numbers().public_numbers.e)
		print("d   ", private_key.private_numbers().d)

		# Encrypt message
		message = b"encrypted data"# randomword(keyLength/8)
		pubkey_tup = (
			private_key.private_numbers().public_numbers.n,
			long(private_key.private_numbers().public_numbers.e)
		)
		puc_key_2ndframework = RSA.construct(pubkey_tup)
		ciphertext = puc_key_2ndframework.encrypt(plain_input, keySize)

		# Dump hex value
		print("\r\nHex value")
		e_str = struct.pack(">I", private_key.private_numbers().public_numbers.e)
		toDump = [[
				FixedBytes(keyLength/8, packl_ctypes(private_key.private_numbers().public_numbers.n)),
				'rsa_n_' + str(keyLength),
			], [
				FixedBytes(4, e_str),
				'rsa_e_' + str(keyLength),
			], [
				FixedBytes(keyLength/8, packl_ctypes(private_key.private_numbers().d)),
				'rsa_d_' + str(keyLength),
			], [
				FixedBytes(keyLength/8, packl_ctypes(private_key.private_numbers().p)),
				'rsa_p_' + str(keyLength),
			], [
				FixedBytes(keyLength/8, packl_ctypes(private_key.private_numbers().q)),
				'rsa_q_' + str(keyLength),
			], [
				FixedBytes(keyLength/8, packl_ctypes(private_key.private_numbers().dmp1)),
				'rsa_dmp1_' + str(keyLength),
			], [
				FixedBytes(keyLength/8, packl_ctypes(private_key.private_numbers().dmq1)),
				'rsa_dmq1_' + str(keyLength),
			], [
				FixedBytes(keyLength/8, packl_ctypes(private_key.private_numbers().iqmp)),
				'rsa_iqmp_' + str(keyLength),
			], [
				FixedBytes(keyLength/8, ciphertext),
				'ciphertext_' + str(keyLength),
			], [
				FixedBytes(keyLength/8, plaintext),
				'plaintext_' + str(keyLength),
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
