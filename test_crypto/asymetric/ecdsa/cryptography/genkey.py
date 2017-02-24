#!/usr/bin/python
# -*- coding: utf-8 -*-

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import utils
import sys

sys.path.insert(0, '../../../../test_bluefinserial/bluefinserial')
from utils import *


#######################################################################
# Constant declaration
#######################################################################
MSG = "abc"


#######################################################################
# Generate the EC keys
#######################################################################
private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())

public_key = private_key.public_key()


#######################################################################
# Dump the private key to PEM file
#######################################################################
serialized_private = private_key.private_bytes(
	encoding=serialization.Encoding.PEM,
	format=serialization.PrivateFormat.PKCS8,
	# encryption_algorithm=serialization.BestAvailableEncryption(b'1234')
	encryption_algorithm=serialization.NoEncryption()
	)
with open("./private.pem", "wb") as f:
	f.write(serialized_private)


#######################################################################
# Dump the public key to PEM file
#######################################################################
serialized_public = public_key.public_bytes(
	encoding=serialization.Encoding.PEM,
	format=serialization.PublicFormat.SubjectPublicKeyInfo
	)
with open("./pub.pem", "wb") as f:
	f.write(serialized_public)


#######################################################################
# Print result to console
#######################################################################
print(private_key.private_numbers().private_value)
dump_hex(packl_ctypes(private_key.private_numbers().private_value), 'Private bytes: ', token=', ', prefix='0x', wrap=8)

print(public_key.public_numbers().x)
dump_hex(packl_ctypes(public_key.public_numbers().x), 'Public X bytes: ', token=', ', prefix='0x', wrap=8)

print(public_key.public_numbers().y)
dump_hex(packl_ctypes(public_key.public_numbers().y), 'Public Y bytes: ', token=', ', prefix='0x', wrap=8)


#######################################################################
# Using the private key to generate the signature of "MSG"
#######################################################################
signature = private_key.sign(
	MSG,
	ec.ECDSA(hashes.SHA256())
	)
dump_hex(signature, 'DER RFC 3279 signature bytes: ', token=', ', prefix='0x', wrap=8)
r_s = utils.decode_dss_signature(signature)
dump_hex(packl_ctypes(r_s[0]), 'Raw r bytes: ', token=', ', prefix='0x', wrap=8)
dump_hex(packl_ctypes(r_s[1]), 'Raw s bytes: ', token=', ', prefix='0x', wrap=8)

#######################################################################
# Using public key to verify the signature
#######################################################################
print("Verify status: ", public_key.verify(signature, MSG, ec.ECDSA(hashes.SHA256())))
