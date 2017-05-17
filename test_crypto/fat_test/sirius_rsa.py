#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-14 23:34:45

# ---- IMPORTS
import re
import time
import serial
import struct
import sys
import git
import os
import inspect
from optparse import OptionParser, OptionGroup
def get_git_root():
	CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep
	path = CURRENT_DIR
	git_repo = git.Repo(path, search_parent_directories=True)
	git_root = git_repo.git.rev_parse("--show-toplevel")
	print (git_root)
	return git_root
sys.path.insert(0, get_git_root() + '/test_bluefinserial/bluefinserial')
from utils import *
from datalink_deliver import *
from scan import scan
from utils import *
from sirius_api_crypto import *


from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Constants
KEY_SIZE = 2048
VALID_TARGET = ["RF", "APP"]

def main():
	parser = OptionParser()
	parser.add_option(  "-s", "--serial",
						dest="serial",
						type="string",
						default=BLUEFINSERIAL_DEFAULT_SERIAL_PORT,
						help="define the serial port to use")
	parser.add_option(  "-b", "--baud",
						dest="baud",
						type="string",
						default=BLUEFINSERIAL_BAUDRATE,
						help="define the serial baudrate to use")
	parser.add_option(  "-t", "--target",
						dest="target",
						default="APP",
						help="Choose type of target to send serial API to, any of: %s" % ', '.join(VALID_TARGET))
	parser.add_option(  "-m", "--message",
						dest="message",
						default="",
						help="the input message to be hashed")
	parser.add_option(  "-d", "--debug",
						dest="debug",
						default=0,
						action="count",
						help="Make the script more verbose")
	(options, args) = parser.parse_args()

	# Init the com port
	try:
		comm = BluefinserialSend(options.serial, options.baud)
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)
	print_ok("Use " + options.serial + " with baudrate = " + str(options.baud))

	sirius_crypto = SiriusAPICrypto(comm)

	KEY_SIZE = [512, 1024, 2048, 3072]

	for idx, keySize in enumerate(KEY_SIZE):
		print_ok("Test RSA with keylength = %d" % keySize)
		#######################################
		# Key generation
		private_key = rsa.generate_private_key(public_exponent=65537, key_size=keySize, backend=default_backend())
		public_key = private_key.public_key()

		#######################################
		# Key download
		rsa_n = packl_ctypes(private_key.private_numbers().public_numbers.n)
		rsa_d = packl_ctypes(private_key.private_numbers().d)
		rsa_p = packl_ctypes(private_key.private_numbers().p)
		rsa_q = packl_ctypes(private_key.private_numbers().q)
		rsa_e = private_key.private_numbers().public_numbers.e
		rsa_n = FixedBytes(keySize/8, rsa_n)
		rsa_d = FixedBytes(keySize/8, rsa_d)
		rsa_p = FixedBytes(keySize/8, rsa_p)
		rsa_q = FixedBytes(keySize/8, rsa_q)

		sirius_crypto.KeyDownload(target=options.target, RSA_n=rsa_n, RSA_d=rsa_d, RSA_e=rsa_e)

		#######################################
		# Doing with rsa
		# encrypt
		plain_input = FixedBytes(keySize/8, options.message)
		# plain_input = options.message
		ciphered = sirius_crypto.Rsa(options.target, "ENC", plain_input)
		ciphered = FixedBytes(keySize/8, ciphered)
		if options.debug >= 1:
			dump_hex(ciphered, "ciphered: ")

		# decrypt
		plain_ret = sirius_crypto.Rsa(options.target, "DEC", ciphered)
		plain_ret = FixedBytes(keySize/8, plain_ret)

		# print result
		if options.debug >= 1:
			dump_hex(plain_ret,   "plain_ret  : ")
			dump_hex(plain_input, "plain_input: ")
		print("Check the plaintext return from board, with our input plaintext: ",
			plain_ret == plain_input)

if __name__ == "__main__":
	main()
