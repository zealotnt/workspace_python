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

	#######################################################
	# Create key and download to board
	# Key generation
	private_key = ec.generate_private_key(
		ec.SECP256K1(), default_backend()
	)
	public_key = private_key.public_key()

	ecdsaPubXStr = packl_ctypes(public_key.public_numbers().x)
	ecdsaPubYStr = packl_ctypes(public_key.public_numbers().y)
	ecdsaPriStr = packl_ctypes(private_key.private_numbers().private_value)
	ecdsaPubXStr = TrimZeroesBytes(KEY_SIZE/8, ecdsaPubXStr)
	ecdsaPubYStr = TrimZeroesBytes(KEY_SIZE/8, ecdsaPubYStr)
	ecdsaPriStr = TrimZeroesBytes(KEY_SIZE/8, ecdsaPriStr)

	sirius_crypto.KeyDownload(target=options.target, ECDSA_x=ecdsaPubXStr, ECDSA_y=ecdsaPubYStr, ECDSA_pri=ecdsaPriStr)

	#######################################################
	# Sign the message
	r_s = sirius_crypto.EcdsaSign(target=options.target, curve="secp256k1", hashAlgo="SHA256", message=options.message)
	sig_r = r_s[:len(r_s)/2]
	sig_s = r_s[len(r_s)/2:]

	# Check the signature return from the sirius board
	signature = utils.encode_dss_signature(
		CalculateBigInt(sig_r),
		CalculateBigInt(sig_s)
	)
	print("Using signature fom sirius, we will verify => status: ", public_key.verify(signature, options.message, ec.ECDSA(hashes.SHA256())))

	#######################################################
	# Verify the message
	# create our own signature
	signature = private_key.sign(
		options.message,
		ec.ECDSA(hashes.SHA256())
	)
	r_s = utils.decode_dss_signature(signature)
	sig_r_str = TrimZeroesBytes(KEY_SIZE/8, packl_ctypes(r_s[0]))
	sig_s_str = TrimZeroesBytes(KEY_SIZE/8, packl_ctypes(r_s[1]))
	sigCombine = sig_r_str + sig_s_str
	verifyStatus = sirius_crypto.EcdsaVerify(
		target=options.target,
		curve="secp256k1",
		hashAlgo="SHA256",
		message=options.message,
		signature=sigCombine
	)
	print("We sign a message using our private key, sirius should return true: ", verifyStatus)

	# Try modify one elem of signature, see if verify failed
	sigCombine = sig_r_str + sig_s_str
	sigNum = chr(ord(sigCombine[0]) + 1)
	sigCombine = sigNum + sigCombine[1:]
	verifyStatus = sirius_crypto.EcdsaVerify(
		target=options.target,
		curve="secp256k1",
		hashAlgo="SHA256",
		message=options.message,
		signature=sigCombine
	)
	print("Modify a signature, sirius should return false: ", verifyStatus)


if __name__ == "__main__":
	main()
