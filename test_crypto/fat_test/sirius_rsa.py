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
	parser.add_option(  "-o", "--operation",
						dest="operation",
						default="ENC",
						help="Choose rsa operation type")
	parser.add_option(  "-m", "--message",
						dest="message",
						default="",
						help="the input message to be hashed")
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

	# Key generation
	private_key = rsa.generate_private_key(public_exponent=65537, key_size=KEY_SIZE, backend=default_backend())
	public_key = private_key.public_key()

	# Key download
	rsa_n = packl_ctypes(private_key.private_numbers().public_numbers.n)
	rsa_d = packl_ctypes(private_key.private_numbers().d)
	rsa_e = private_key.private_numbers().public_numbers.e
	rsa_n = TrimZeroesBytes(KEY_SIZE/8, rsa_n)
	rsa_d = TrimZeroesBytes(KEY_SIZE/8, rsa_d)

	sirius_crypto.KeyDownload(target=options.target, RSA_n=rsa_n, RSA_d=rsa_d, RSA_e=rsa_e)
	sirius_crypto.Rsa(options.target, options.operation, options.message)

if __name__ == "__main__":
	main()