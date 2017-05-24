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
	parser.add_option(  "-g", "--gendata",
						dest="gendata",
						default=None,
						help="Option to generate cmac standard data, instead of running real test")
	parser.add_option(  "--dumpStyle",
						dest="dumpStyle",
						default="C",
						help="Style to dump C|raw")

	(options, args) = parser.parse_args()

	# K, M and T from
	# http://csrc.nist.gov/publications/nistpubs/800-38B/Updated_CMAC_Examples.pdf
	# http://csrc.nist.gov/groups/ST/toolkit/examples.html
	# http://csrc.nist.gov/groups/ST/toolkit/documents/Examples/AES_CMAC.pdf
	# http://csrc.nist.gov/groups/ST/toolkit/documents/Examples/TDES_CMAC.pdf
	# D.1 AES-128
	testCase_E2_AES_128 = {
		# K: 2b7e1516 28aed2a6 abf71588 09cf4f3c
		# M: 6bc1bee2 2e409f96 e93d7e11 7393172a Mlen: 128
		# expected result
		# T: 070a16b4 6b4d4144 f79bdd9d d04a287c
		"name": "E2_AES_128",
		"cipher": "AES",
		"K": '\x2b\x7e\x15\x16\x28\xae\xd2\xa6\xab\xf7\x15\x88\x09\xcf\x4f\x3c',
		"M": '\x6b\xc1\xbe\xe2\x2e\x40\x9f\x96\xe9\x3d\x7e\x11\x73\x93\x17\x2a',
		"T": '\x07\x0a\x16\xb4\x6b\x4d\x41\x44\xf7\x9b\xdd\x9d\xd0\x4a\x28\x7c',
	}

	testCase_E2_AES_192 = {
		# K: 8E73B0F7 DA0E6452 C810F32B 809079E5 62F8EAD2 522C6B7B
		# M: 6BC1BEE2 2E409F96 E93D7E11 7393172A
		# expected result
		# T: 9E99A7BF 31E71090 0662F65E 617C5184
		"name": "E2_AES_192",
		"cipher": "AES",
		"K": '\x8E\x73\xB0\xF7\xDA\x0E\x64\x52\xC8\x10\xF3\x2B\x80\x90\x79\xE5\x62\xF8\xEA\xD2\x52\x2C\x6B\x7B',
		"M": '\x6b\xc1\xbe\xe2\x2e\x40\x9f\x96\xe9\x3d\x7e\x11\x73\x93\x17\x2a',
		"T": '\x9E\x99\xA7\xBF\x31\xE7\x10\x90\x06\x62\xF6\x5E\x61\x7C\x51\x84',
	}

	testCase_E2_AES_256 = {
		# K: 603DEB10 15CA71BE 2B73AEF0 857D7781 1F352C07 3B6108D7 2D9810A3 0914DFF4
		# M: 6BC1BEE2 2E409F96 E93D7E11 7393172A
		# expected result
		# T: 28A7023F 452E8F82 BD4BF28D 8C37C35C
		"name": "E2_AES_256",
		"cipher": "AES",
		"K": '\x60\x3D\xEB\x10\x15\xCA\x71\xBE\x2B\x73\xAE\xF0\x85\x7D\x77\x81\x1F\x35\x2C\x07\x3B\x61\x08\xD7\x2D\x98\x10\xA3\x09\x14\xDF\xF4',
		"M": '\x6b\xc1\xbe\xe2\x2e\x40\x9f\x96\xe9\x3d\x7e\x11\x73\x93\x17\x2a',
		"T": '\x28\xA7\x02\x3F\x45\x2E\x8F\x82\xBD\x4B\xF2\x8D\x8C\x37\xC3\x5C',
	}

	testCase_S1_TDES = {
		# Key1 is
		#  01234567 89ABCDEF
		# Key2 is
		#  23456789 ABCDEF01
		# Key3 is
		#  456789AB CDEF0123
		#
		# Sample #2
		# Plaintext is
		#  6BC1BEE2 2E409F96 E93D7E11 7393172A
		# Tag is
		# 30239CF1 F52E6609

		"name": "S1_TDES",
		"cipher": "TDES",
		"K": '\x01\x23\x45\x67\x89\xAB\xCD\xEF\x23\x45\x67\x89\xAB\xCD\xEF\x01\x45\x67\x89\xAB\xCD\xEF\x01\x23',
		"M": '\x6B\xC1\xBE\xE2\x2E\x40\x9F\x96\xE9\x3D\x7E\x11\x73\x93\x17\x2A',
		"T": '\x30\x23\x9C\xF1\xF5\x2E\x66\x09',
	}
	testCases = [testCase_E2_AES_128, testCase_E2_AES_192, testCase_E2_AES_256, testCase_S1_TDES]

	dumpFileText = ""
	# Just gen data, no sending command
	if options.gendata is not None:
		for item in testCases:
			dumpFileText += dump_hex(
				item["M"],
				"%s_%s" % (item["name"], "InputMessage"),
				preFormat=options.dumpStyle
			)
			dumpFileText += dump_hex(
				item["K"],
				"%s_%s" % (item["name"], "Key"),
				preFormat=options.dumpStyle
			)
			dumpFileText += dump_hex(
				item["T"],
				"%s_%s" % (item["name"], "OutTag"),
				preFormat=options.dumpStyle
			)

		dumpFileText = "#include <stdint.h>\r\n\r\n" + dumpFileText
		print("dump ne", dumpFileText, options.gendata)
		f = open(options.gendata, "w")
		f.write(dumpFileText)
		f.close()
	# Send command, no gen data
	else:
		# Init the com port
		try:
			comm = BluefinserialSend(options.serial, options.baud)
		except Exception, e:
			print e
			parser.print_help()
			sys.exit(-1)
		print_ok("Use " + options.serial + " with baudrate = " + str(options.baud))

		sirius_crypto = SiriusAPICrypto(comm)

		for item in testCases:
			cmac = sirius_crypto.Cmac(options.target, item["cipher"], item["K"], item["M"])
			if cmac == item["T"]:
				print_ok("Test case " + item["name"] + " ok")
			else:
				print_err("Test case " + item["name"] + " fail:")
				dump_hex(item["T"], "Expected: ")
				dump_hex(cmac,      "Result  : ")
				sys.exit(-1)

if __name__ == "__main__":
	main()
