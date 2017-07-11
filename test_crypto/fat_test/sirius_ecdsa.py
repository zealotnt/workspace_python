#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-12 14:08:01

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

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import utils

KEY_SIZE = 256
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
						default=os.urandom(KEY_SIZE),
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

	HASH_ALGO_SIRIUS = [ "SHA1", "SHA256" ]
	HASH_ALGO_NATIVE = [hashes.SHA1(), hashes.SHA256()]

	for idx, hashAlgo in enumerate(HASH_ALGO_SIRIUS):
		print("")
		print_ok(">"*40)
		print_ok("Test ECDSA with hash = %s" % hashAlgo)

		#######################################################
		# Create key and download to board
		# Key generation
		private_key = ec.generate_private_key(
			ec.SECP256R1(), default_backend()
		)
		public_key = private_key.public_key()

		ecdsaPubXStr = packl_ctypes(public_key.public_numbers().x)
		ecdsaPubYStr = packl_ctypes(public_key.public_numbers().y)
		ecdsaPriStr = packl_ctypes(private_key.private_numbers().private_value)
		ecdsaPubXStr = FixedBytes(KEY_SIZE/8, ecdsaPubXStr)
		ecdsaPubYStr = FixedBytes(KEY_SIZE/8, ecdsaPubYStr)
		ecdsaPriStr = FixedBytes(KEY_SIZE/8, ecdsaPriStr)
		if options.debug >= 2:
			dump_hex(ecdsaPubXStr, "ecdsaPubXStr: ")
			dump_hex(ecdsaPubYStr, "ecdsaPubYStr: ")
			dump_hex(ecdsaPriStr,  "ecdsaPriStr : ")
		sirius_crypto.KeyDownload(target=options.target, ECDSA_x=ecdsaPubXStr, ECDSA_y=ecdsaPubYStr, ECDSA_pri=ecdsaPriStr)

		#######################################################
		# Sign functionality test on sirius
		# let the sirius board sign the message
		r_s = sirius_crypto.EcdsaSign(target=options.target, curve="secp256k1", hashAlgo=hashAlgo, message=options.message)
		sig_r = r_s[:len(r_s)/2]
		sig_s = r_s[len(r_s)/2:]

		# Check the signature return from the sirius board, using native verification
		signature = utils.encode_dss_signature(
			CalculateBigInt(sig_r),
			CalculateBigInt(sig_s)
		)
		if options.debug >= 2:
			dump_hex(r_s, "Signature receive: ")
		print("Using signature fom sirius, we will verify => status: ",
			public_key.verify(
				signature,
				options.message,
				ec.ECDSA(HASH_ALGO_NATIVE[idx])
			)
		)

		#######################################################
		# Verification functionality test on sirius
		# create native own signature
		signature = private_key.sign(
			options.message,
			ec.ECDSA(HASH_ALGO_NATIVE[idx])
		)
		r_s = utils.decode_dss_signature(signature)
		sig_r_str = FixedBytes(KEY_SIZE/8, packl_ctypes(r_s[0]))
		sig_s_str = FixedBytes(KEY_SIZE/8, packl_ctypes(r_s[1]))
		sigCombine = sig_r_str + sig_s_str
		if options.debug >= 2:
			dump_hex(sig_r_str, "our sig_r_str: ")
			dump_hex(sig_s_str, "our sig_s_str: ")

		# send our native signature, let the target check the signature is valid or not
		verifyStatus = sirius_crypto.EcdsaVerify(
			target=options.target,
			curve="secp256k1",
			hashAlgo=hashAlgo,
			message=options.message,
			signature=sigCombine
		)
		if verifyStatus != True:
			print_err("We sign a message using our private key, sirius tell this is a invalid signature, fail")
		else:
			print("We sign a message using our private key, sirius tell this is a valid signature, pass")

		# Try modify one elem of signature, see if verify failed
		sigCombine = sig_r_str + sig_s_str
		sigNum = chr(ord(sigCombine[0]) + 1)
		sigCombine = sigNum + sigCombine[1:]
		verifyStatus = sirius_crypto.EcdsaVerify(
			target=options.target,
			curve="secp256k1",
			hashAlgo=hashAlgo,
			message=options.message,
			signature=sigCombine
		)
		if verifyStatus != False:
			print_err("Modify a signature, sirius tell this is a valid signature, fail")
		else:
			print("Modify a signature, sirius tell this an invalid siganture, pass")

		print_ok("<"*40)
		print("")

if __name__ == "__main__":
	main()
