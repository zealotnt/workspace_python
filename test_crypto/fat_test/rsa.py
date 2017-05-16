#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-09 09:44:43


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

# To generate random message
import random, string

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Constants
KEYLENGTH = 2048

# [Source](http://stackoverflow.com/questions/2030053/random-strings-in-python)
def randomword(length):
	randomStr = ''.join(random.choice(string.lowercase) for i in range(length))
	print(len(randomStr))
	return randomStr

def main():
	filePathSave = ""
	if len(sys.argv) == 2:
		filePathSave = sys.argv[1]

	# Key generation
	private_key = rsa.generate_private_key(public_exponent=65537, key_size=KEYLENGTH, backend=default_backend())
	public_key = private_key.public_key()

	# Key dumping
	print("p*q ", private_key.private_numbers().p * private_key.private_numbers().q)
	print("n   ", private_key.private_numbers().public_numbers.n)
	print("e   ", private_key.private_numbers().public_numbers.e)
	print("d   ", private_key.private_numbers().d)

	# Encrypt message
	message = b"encrypted data"# randomword(KEYLENGTH/8)
	ciphertext = public_key.encrypt(
		message,
		padding.OAEP(
			mgf=padding.MGF1(algorithm=hashes.SHA1()),
			algorithm=hashes.SHA1(),
			label=None
		)
	)

	# Decrypt message
	plaintext = private_key.decrypt(
		ciphertext,
		padding.OAEP(
			mgf=padding.MGF1(algorithm=hashes.SHA1()),
			algorithm=hashes.SHA1(),
			label=None
		)
	)
	plaintext == message


	# Sign message
	signature = private_key.sign(
		message,
		padding.PSS(
			mgf=padding.MGF1(hashes.SHA256()),
			salt_length=padding.PSS.MAX_LENGTH
		),
		hashes.SHA256()
	)

	# Verify message
	public_key.verify(
		signature,
		message,
		padding.PSS(
			mgf=padding.MGF1(hashes.SHA256()),
			salt_length=padding.PSS.MAX_LENGTH
		),
		hashes.SHA256()
	)


	# Dump hex value
	print("\r\nHex value")
	dumpFileText = dump_hex(
		packl_ctypes(private_key.private_numbers().public_numbers.n),
		'rsa_n',
		preFormat="C"
	)
	dumpFileText += dump_hex(
		hex(private_key.private_numbers().public_numbers.e),
		'rsa_e',
		preFormat="C"
	)
	dumpFileText += dump_hex(
		packl_ctypes(private_key.private_numbers().d),
		'rsa_d',
		preFormat="C"
	)
	dumpFileText += dump_hex(
		packl_ctypes(private_key.private_numbers().p),
		'rsa_p',
		preFormat="C"
	)
	dumpFileText += dump_hex(
		packl_ctypes(private_key.private_numbers().q),
		'rsa_q',
		preFormat="C"
	)
	dumpFileText += dump_hex(
		ciphertext,
		'ciphertext',
		preFormat="C"
	)
	dumpFileText += dump_hex(
		FixedBytes(KEYLENGTH/8, plaintext),
		'plaintext',
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
