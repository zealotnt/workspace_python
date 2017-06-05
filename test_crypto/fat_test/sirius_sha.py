#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-12 10:41:26

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

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

VALID_HASH = SiriusAPICrypto.getShaMethodList()
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

	digestEngine = [
		hashes.Hash(hashes.SHA1(), backend=default_backend()),
		hashes.Hash(hashes.SHA224(), backend=default_backend()),
		hashes.Hash(hashes.SHA256(), backend=default_backend()),
		hashes.Hash(hashes.SHA384(), backend=default_backend()),
		hashes.Hash(hashes.SHA512(), backend=default_backend()),
	]
	DIGEST_ALGOS = ["SHA1", "SHA224", "SHA256", "SHA384", "SHA512"]
	for idx, digest in enumerate(DIGEST_ALGOS):
		# print the head of resulr
		print("")
		print_ok(">"*40)
		print_ok("Testing %s" % (digest))

		# get digest from sirius
		digest_sirius = sirius_crypto.Sha(options.target, digest, options.message)

		# self calculate
		digestEngine[idx].update(options.message)
		digest_self = digestEngine[idx].finalize()

		# compare with result from sirius
		if digest_sirius != digest_self:
			print_err("digest_sirius != digest_self:")
			dump_hex(digest_sirius, "\tdigest_sirius: ")
			dump_hex(digest_self,   "\tdigest_self  : ")
			continue
		else:
			print_ok("Digest %s ok" % (digest))

		# print the tail of result
		if options.debug >= 1:
			dump_hex(digest_sirius, "\tdigest_sirius: ")
			dump_hex(digest_self,   "\tdigest_self  : ")
		print_ok("<"*40)
		print("")

if __name__ == "__main__":
	main()
