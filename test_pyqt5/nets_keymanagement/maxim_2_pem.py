#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import utils

import array
import sys
sys.path.insert(0, '../../test_bluefinserial/bluefinserial')
from utils import *

def removeNewLine(inputStr):
	inputStr = inputStr.replace('\r', '')
	inputStr = inputStr.replace('\n', '')
	return inputStr

if len(sys.argv) != 3:
	print("Error, usage:")
	print("%s <maxim-key-file> <output-pem-file>" % sys.argv[0])
	sys.exit(-1)

maxim_file = sys.argv[1]
output_pem = sys.argv[2]

with open(maxim_file, 'r') as f:
	private_val_str = f.readline()
	pub_x_str = f.readline()
	pub_y_str = f.readline()

private_val_str = removeNewLine(private_val_str)
pub_x_str = removeNewLine(pub_x_str)
pub_y_str = removeNewLine(pub_y_str)

private_val_bytes = bytes.fromhex(private_val_str)
pub_x_val_bytes = bytes.fromhex(pub_x_str)
pub_y_val_bytes = bytes.fromhex(pub_y_str)

# dump_hex(bytesToBigInt(private_val_bytes), 'pri bytes: ', token=', ', prefix='0x', wrap=8)
# dump_hex(bytesToBigInt(pub_x_val_bytes), 'x bytes: ', token=', ', prefix='0x', wrap=8)
# dump_hex(bytesToBigInt(pub_y_val_bytes), 'y bytes: ', token=', ', prefix='0x', wrap=8)

private_val_int = bytesToBigInt(private_val_bytes)
pub_x_val_int = bytesToBigInt(pub_x_val_bytes)
pub_y_val_int = bytesToBigInt(pub_y_val_bytes)

publicNumber = ec.EllipticCurvePublicNumbers(
	pub_x_val_int,
	pub_y_val_int,
	ec.SECP256R1()
	)

privateNumber = ec.EllipticCurvePrivateNumbers(
	private_val_int,
	publicNumber
	)

privateKey = privateNumber.private_key(default_backend())

serialized_private = privateKey.private_bytes(
	encoding=serialization.Encoding.PEM,
	format=serialization.PrivateFormat.PKCS8,
	# encryption_algorithm=serialization.BestAvailableEncryption(str.encode('1234'))
	encryption_algorithm=serialization.NoEncryption()
	)
with open(output_pem, "wb") as f:
	f.write(serialized_private)
