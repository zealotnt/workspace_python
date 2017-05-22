#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-14 23:34:33

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
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives.asymmetric import utils


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
						help="the input message to be process with dsa")
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

	KEY_SIZE_LENGTHS = [ 1024, 2048 ]
	HASH_ALGO = [hashes.SHA1(), hashes.SHA256()]
	DSA_SIG_PART_LENS = [ 20, 32 ]

	# KEY_SIZE = 3072
	# HASH_ALGO = hashes.SHA256()
	# DSA_SIG_PART_LEN = 32 # r or s

	for idx, KEY_SIZE in enumerate(KEY_SIZE_LENGTHS):
		print("")
		print_ok(">"*40)
		print_ok("Test DSA with keylength = %d" % KEY_SIZE)

		#######################################################
		# Create key and download to board
		# Key generation
		private_key = dsa.generate_private_key(
			key_size=KEY_SIZE, backend=default_backend()
		)
		public_key = private_key.public_key()

		dsa_pStr = packl_ctypes(private_key.public_key().public_numbers().parameter_numbers.p)
		dsa_qStr = packl_ctypes(private_key.public_key().public_numbers().parameter_numbers.q)
		dsa_gStr = packl_ctypes(private_key.public_key().public_numbers().parameter_numbers.g)
		dsa_yStr = packl_ctypes(private_key.public_key().public_numbers().y)
		dsa_xStr = packl_ctypes(private_key.private_numbers().x)

		dsa_pStr = FixedBytes(KEY_SIZE/8, dsa_pStr)
		dsa_qStr = TrimZeroes(dsa_qStr)
		dsa_gStr = FixedBytes(KEY_SIZE/8, dsa_gStr)
		dsa_yStr = FixedBytes(KEY_SIZE/8, dsa_yStr)
		dsa_xStr = TrimZeroes(dsa_xStr)

		if options.debug >= 2:
			dump_hex(dsa_pStr, "dsa_pStr : ")
			dump_hex(dsa_qStr, "dsa_qStr : ")
			dump_hex(dsa_gStr, "dsa_gStr : ")
			dump_hex(dsa_yStr, "dsa_yStr : ")
			dump_hex(dsa_xStr, "dsa_xStr : ")

		sirius_crypto.KeyDownload(
			target=options.target,
			DSS_p=dsa_pStr,
			DSS_q=dsa_qStr,
			DSS_g=dsa_gStr,
			DSS_y=dsa_yStr,
			DSS_x=dsa_xStr
		)

		# #######################################################
		# Sign the message
		# ask the sirius to sign the message
		r_s = sirius_crypto.DsaSign(target=options.target, hashAlgo="SHA256", message=options.message)
		sig_r = r_s[:len(r_s)/2]
		sig_s = r_s[len(r_s)/2:]
		if options.debug >= 2:
			dump_hex(sig_r, "sirius sig_r: ")
			dump_hex(sig_s, "sirius sig_s: ")

		# Check the signature return from the sirius board
		signature = utils.encode_dss_signature(
			CalculateBigInt(sig_r),
			CalculateBigInt(sig_s)
		)
		print("Using signature fom sirius, we will verify => status: (if None means ok)",
			public_key.verify(
				signature,
				options.message,
				HASH_ALGO[idx]
			)
		)

		#######################################################
		# Verify the message
		# create our own signature
		signature = private_key.sign(
			options.message,
			HASH_ALGO[idx]
		)
		r_s = utils.decode_dss_signature(signature)
		sig_r_str = FixedBytes(DSA_SIG_PART_LENS[idx], packl_ctypes(r_s[0]))
		sig_s_str = FixedBytes(DSA_SIG_PART_LENS[idx], packl_ctypes(r_s[1]))
		sigCombine = sig_r_str + sig_s_str
		if options.debug >= 2:
			dump_hex(sig_r_str, "our sig_r_str: ")
			dump_hex(sig_s_str, "our sig_s_str: ")

		# ask sirius to verify our generated signature
		verifyStatus = sirius_crypto.DsaVerify(
			target=options.target,
			hashAlgo="SHA256",
			message=options.message,
			signature=sigCombine
		)
		print("We sign a message using our private key, sirius should return true: ", verifyStatus)

		# Try modify one elem of signature, see if verify failed
		sigCombine = sig_r_str + sig_s_str
		sigNum = chr(ord(sigCombine[0]) + 1)
		sigCombine = sigNum + sigCombine[1:]
		verifyStatus = sirius_crypto.DsaVerify(
			target=options.target,
			hashAlgo="SHA256",
			message=options.message,
			signature=sigCombine
		)
		print("Modify a signature, sirius should return false: ", verifyStatus)
		print_ok("<"*40)
		print("")

if __name__ == "__main__":
	main()
