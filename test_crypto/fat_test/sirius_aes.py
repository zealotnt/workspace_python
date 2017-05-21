#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-14 23:34:08

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

from Crypto.Cipher import AES

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

	# For PyCrypto package
	cryptoMode = [AES.MODE_ECB, AES.MODE_CBC, AES.MODE_OFB, AES.MODE_CFB]
	segmentSize = [None, None, 128, 128]
	# For looping
	modes = ["ECB", "CBC", "OFB", "CFB"]
	keyLengths = [16, 24, 32]
	for idx, mode in enumerate(modes):
		for keyLen in keyLengths:
			print("")
			print_ok(">"*40)
			print_ok("Testing AES_%s with keylen=%d" % (mode, keyLen))

			iv = os.urandom(16)
			key = os.urandom(keyLen)
			data = os.urandom(32)

			if options.debug >= 2:
				dump_hex(data, "data: ")
				dump_hex(iv,   "iv  : ")
				dump_hex(key,  "key : ")

			# Try encrypt with sirius
			ciphered = sirius_crypto.Aes(target=options.target, en_dec="ENC", mode=mode, iv=iv, key=key, data=data)
			# Check with our result
			if segmentSize[idx] is not None:
				encryption_suite = AES.new(key, cryptoMode[idx], iv, segment_size=segmentSize[idx])
			else:
				encryption_suite = AES.new(key, cryptoMode[idx], iv)
			cipher_self = encryption_suite.encrypt(data)
			if options.debug >= 1:
				dump_hex(cipher_self, "cipher_self: ")
			if cipher_self != ciphered:
				print_err("Verify ciphered and cipher_self: fail")
			else:
				print("Verify ciphered and cipher_self: pass")

			# Try decrypt with sirius
			de_ciphered = sirius_crypto.Aes(target=options.target, en_dec="DEC", mode=mode, iv=iv, key=key, data=ciphered)
			if options.debug >= 1:
				dump_hex(ciphered,    "ciphered   : ")
				dump_hex(de_ciphered, "de_ciphered: ")

			# If it same as input message, test case is pass
			if de_ciphered != data:
				print_err("Verify input data with the de_ciphered from sirius: fail")
			else:
				print("Verify input data with the de_ciphered from sirius: pass")
			print_ok("<"*40)
			print("")

if __name__ == "__main__":
	main()
