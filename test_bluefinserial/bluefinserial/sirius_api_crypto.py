#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-12 10:52:38

#---- IMPORTS
import os
import serial
import struct
import binascii
import time
import sys

from crc8 import crc8
from utils import *
from datalink_deliver import *

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

#---- CLASSES
class SiriusAPICrypto():
	"""
	SiriusAPICrypto class, implement crypto API of Sirius
	"""
	VERBOSE=False
	sha_dict = {
		"SHA1": 0,
		"SHA224": 1,
		"SHA256": 2,
		"SHA384": 3,
		"SHA512": 4,
	}
	sha_functions = {
		"SHA1": hashes.SHA1(),
		"SHA224": hashes.SHA224(),
		"SHA256": hashes.SHA256(),
		"SHA384": hashes.SHA384(),
		"SHA512": hashes.SHA512(),
	}

	def __init__(self, bluefin_serial, verbose=False):
		"""
		"""
		self._datalink = bluefin_serial
		self.VERBOSE = verbose

	@staticmethod
	def getShaMethodList():
		ret = []
		for key in SiriusAPICrypto.sha_dict:
			ret.append(key)
		return ret

	@staticmethod
	def getShaMethodStr():
		return ', '.join(['%s' % (key) for (key, value) in SiriusAPICrypto.sha_dict.items()])

	def Sha(self, method, message, target):
		"""
		SHA digest API
		method: <str> method of hashing
		message: <str> message to be hased
		isApp: <bool> if true, will send to Application processor
		"""
		sirius_target = BluefinserialCommand.TARGET_APPLICATION if target == "APP" else BluefinserialCommand.TARGET_RF
		pkt = BluefinserialCommand(sirius_target)
		sha_package = struct.pack('<B', SiriusAPICrypto.sha_dict[method]) + message
		cmd = pkt.Packet('\x8b', '\x4d', sha_package)
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("Sha serial API fail, code 0x%02x" % ord(rsp[2]))
			return None

		# Check with our result
		digest = hashes.Hash(SiriusAPICrypto.sha_functions[method], backend=default_backend())
		digest.update(message)
		ourResult = digest.finalize()
		theirResult = rsp[3:]
		if len(theirResult) != len(ourResult):
			print_err("Wrong length, our: %d, their: %d" % (len(ourResult), len(theirResult)))
			return None
		if theirResult != ourResult:
			print_err("Wrong value")
			dump_hex(ourResult,   "Ours:   ")
			dump_hex(theirResult, "Theirs: ")
			return None
		dump_hex(rsp[3:], "Sha serial return ok, check ok, digest: ")
		return True
