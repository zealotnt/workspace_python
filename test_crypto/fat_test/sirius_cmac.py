#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-14 23:32:36

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
						help="the input message to be cmac")
	parser.add_option(  "-c", "--cipher",
						dest="cipher",
						default="AES",
						help="cipher operation with cmac")
	parser.add_option(  "-p", "--password",
						dest="key",
						default=os.urandom(16),
						help="key to used with cmac")
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


	# K, M and T from
	# http://csrc.nist.gov/publications/nistpubs/800-38B/Updated_CMAC_Examples.pdf
	# D.1 AES-128
	testCase_D1_AES_128 = {
		# K: 2b7e1516 28aed2a6 abf71588 09cf4f3c
		# M: 6bc1bee2 2e409f96 e93d7e11 7393172a Mlen: 128
		# expected result
		# T = 070a16b4 6b4d4144 f79bdd9d d04a287c
		"name": "D1_AES_128",
		"K": '\x2b\x7e\x15\x16\x28\xae\xd2\xa6\xab\xf7\x15\x88\x09\xcf\x4f\x3c',
		"M": '\x6b\xc1\xbe\xe2\x2e\x40\x9f\x96\xe9\x3d\x7e\x11\x73\x93\x17\x2a',
		"T": '\x07\x0a\x16\xb4\x6b\x4d\x41\x44\xf7\x9b\xdd\x9d\xd0\x4a\x28\x7c',
	}
	testCases = [testCase_D1_AES_128]

	for item in testCases:
		cmac = sirius_crypto.Cmac(options.target, options.cipher, item["K"], item["M"])
		if cmac == item["T"]:
			print_ok("Test case " + item["name"] + " ok")
		else:
			print_ok("Test case " + item["name"] + " fail")
			sys.exit(-1)

if __name__ == "__main__":
	main()
