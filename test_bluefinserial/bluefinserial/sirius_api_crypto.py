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

	# SHA
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

	# ECDSA
	ecdsa_curve = {
		"secp256k1": 0,
		"secp256r1": 0,
	}
	ecdsa_sha_functions = {
		"SHA1": 0,
		"SHA256": 1,
	}

	# DSA
	dsa_sha_functions = {
		"SHA1": 0,
		"SHA256": 1,
	}

	# AES
	aes_key_length = [16, 24, 32]
	aes_mode = {
		"ECB_ENC":	0,
		"ECB_DEC":	1,
		"CBC_ENC":	2,
		"CBC_DEC":	3,
		"OFB_ENC":	4,
		"OFB_DEC":	5,
		"CFB_ENC":	6,
		"CFB_DEC":	7,
	}
	aes_block_size = 16

	# TDES
	tdes_key_length = [8, 16, 24]
	tdes_mode = {
		"ECB_ENC":	0,
		"ECB_DEC":	1,
		"CBC_ENC":	2,
		"CBC_DEC":	3,
		"OFB_ENC":	4,
		"OFB_DEC":	5,
		"CFB_ENC":	6,
		"CFB_DEC":	7,
	}
	tdes_block_size = 8

	# CMAC
	cmac_operation = {
		"TDES": 0,
		"AES": 1,
	}
	cmac_key_length = {
		"TDES": tdes_key_length,
		"AES": aes_key_length
	}

	# RSA
	rsa_operations = {
		"ENC": 0,
		"DEC": 1,
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

	def Trng(self, target, numberOfBytes):
		"""

		"""
		sirius_target = BluefinserialCommand.TARGET_APPLICATION if target == "APP" else BluefinserialCommand.TARGET_RF
		pkt = BluefinserialCommand(sirius_target)
		trng_package = struct.pack('<B', numberOfBytes)
		cmd = pkt.Packet('\x8b', '\x0e', trng_package)
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("Trng serial API fail, code 0x%02x" % ord(rsp[2]))
			return None

		return rsp[3:]

	def Sha(self, target, method, message, selfCheck=False, verbose=False):
		"""
		SHA digest API
		method: <str> method of hashing
		message: <str> message to be hased
		isApp: <bool> if true, will send to Application processor
		"""
		if method not in SiriusAPICrypto.sha_dict:
			print_err("Invalid method: %s" % method)
			return None
		sirius_target = BluefinserialCommand.TARGET_APPLICATION if target == "APP" else BluefinserialCommand.TARGET_RF
		pkt = BluefinserialCommand(sirius_target, verbose=verbose)
		sha_package = struct.pack('<B', SiriusAPICrypto.sha_dict[method]) + message
		cmd = pkt.Packet('\x8b', '\x4e', sha_package)
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("Sha serial API fail, code 0x%02x" % ord(rsp[2]))
			return None

		# Check with our result
		if selfCheck:
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
		if verbose:
			dump_hex(rsp[3:], "Sha serial return: ")
		return rsp[3:]

	def KeyDownload(self, target, DSS_p=None, DSS_q=None, DSS_g=None, DSS_y=None, DSS_x=None,
					ECDSA_x=None, ECDSA_y=None, ECDSA_pri=None,
					RSA_p=None, RSA_q=None, RSA_n=None, RSA_d=None, RSA_e=None, verbose=False):
		info = MlsKeyTlv(verbose=self.VERBOSE)

		if DSS_p is not None:
			info.AddValList('DSS_p', DSS_p)
		if DSS_q is not None:
			info.AddValList('DSS_q', DSS_q)
		if DSS_g is not None:
			info.AddValList('DSS_g', DSS_g)
		if DSS_y is not None:
			info.AddValList('DSS_y', DSS_y)
		if DSS_x is not None:
			info.AddValList('DSS_x', DSS_x)
		if ECDSA_x is not None:
			info.AddValList('ECDSA_x', ECDSA_x)
		if ECDSA_y is not None:
			info.AddValList('ECDSA_y', ECDSA_y)
		if ECDSA_pri is not None:
			info.AddValList('ECDSA_pri', ECDSA_pri)
		if RSA_n is not None:
			info.AddValList('RSA_n', RSA_n)
		if RSA_d is not None:
			info.AddValList('RSA_d', RSA_d)
		if RSA_p is not None:
			info.AddValList('RSA_p', RSA_p)
		if RSA_q is not None:
			info.AddValList('RSA_q', RSA_q)
		if RSA_e is not None:
			# RSA_e should be a number
			if isinstance(RSA_e, int ):
				RSA_e_str = struct.pack('>I', RSA_e)
				info.AddValList('RSA_e', RSA_e_str)
			elif isinstance(RSA_e, str ):
				info.AddValList('RSA_e', RSA_e)
			else:
				print_err("Invalid value of RSA_e, abort")
				return None

		sirius_target = BluefinserialCommand.TARGET_APPLICATION if target == "APP" else BluefinserialCommand.TARGET_RF

		for item in info.ValList():
			pkt = BluefinserialCommand(sirius_target, verbose=verbose)
			cmd = pkt.Packet('\x8b', '\x46', item)
			rsp = self._datalink.Exchange(cmd)
			if (rsp is None):
				print_err("Send fail")
				return None
			if rsp[2] != '\x00':
				print_err("Key download fail, code 0x%02x" % ord(rsp[2]))
				return None
		return True

	def EcdsaSign(self, target, curve, hashAlgo, message, verbose=False):
		"""
		return:
		+ signature if success
		+ None if fail
		"""
		if curve not in SiriusAPICrypto.ecdsa_curve:
			print_err("Invalid curve: %s" % curve)
			return None
		if hashAlgo not in SiriusAPICrypto.ecdsa_sha_functions:
			print_err("Invalid hash: %s" % hashAlgo)
			return None

		sirius_target = BluefinserialCommand.TARGET_APPLICATION if target == "APP" else BluefinserialCommand.TARGET_RF

		pkt = BluefinserialCommand(sirius_target, verbose=verbose)
		ecdsa_sign_package = struct.pack('<BBBHB',
			0, # operation: sign
			SiriusAPICrypto.ecdsa_curve[curve], # curve
			SiriusAPICrypto.ecdsa_sha_functions[hashAlgo], # sha
			len(message), # message len
			0 # no signature
		) + message

		cmd = pkt.Packet('\x8b', '\x4a', ecdsa_sign_package)
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("ECDSA sign fail, code 0x%02x" % ord(rsp[2]))
			return None
		if verbose:
			dump_hex(rsp[3:], "signature: ")
		return rsp[3:]

	def EcdsaVerify(self, target, curve, hashAlgo, message, signature, verbose=False):
		"""
		return:
		+ True if verify ok
		+ False if verify fail
		+ None if communication error
		"""
		if curve not in SiriusAPICrypto.ecdsa_curve:
			print_err("Invalid curve: %s" % curve)
			return None
		if hashAlgo not in SiriusAPICrypto.ecdsa_sha_functions:
			print_err("Invalid hash: %s" % hashAlgo)
			return None

		sirius_target = BluefinserialCommand.TARGET_APPLICATION if target == "APP" else BluefinserialCommand.TARGET_RF

		pkt = BluefinserialCommand(sirius_target, verbose=verbose)
		ecdsa_sign_package = struct.pack('<BBBHB',
			1, # operation: verify
			SiriusAPICrypto.ecdsa_curve[curve], # curve
			SiriusAPICrypto.ecdsa_sha_functions[hashAlgo], # sha
			len(message), # message len
			len(signature) # no signature
		) + message + signature

		cmd = pkt.Packet('\x8b', '\x4a', ecdsa_sign_package)
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("ECDSA verify fail, code 0x%02x" % ord(rsp[2]))
			return None
		if verbose:
			print("Verify status: %s" % ("ok" if ord(rsp[3]) == 0 else "failed"))
		return True if ord(rsp[3]) == 0 else False

	def DsaSign(self, target, hashAlgo, message, verbose=False):
		"""
		return:
		+ signature if success
		+ None if fail
		"""
		if hashAlgo not in SiriusAPICrypto.dsa_sha_functions:
			print_err("Invalid hash: %s" % curve)
			return None

		sirius_target = BluefinserialCommand.TARGET_APPLICATION if target == "APP" else BluefinserialCommand.TARGET_RF

		pkt = BluefinserialCommand(sirius_target, verbose=False)
		dsa_sign_package = struct.pack('<BBHB',
			0, # operation: sign
			SiriusAPICrypto.dsa_sha_functions[hashAlgo], # sha
			len(message), # message len
			0 # no signature
		) + message

		cmd = pkt.Packet('\x8b', '\x48', dsa_sign_package)
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("DSA sign fail, code 0x%02x" % ord(rsp[2]))
			return None
		if verbose:
			dump_hex(rsp[3:], "signature: ")
		return rsp[3:]

	def DsaVerify(self, target, hashAlgo, message, signature, verbose=False):
		"""
		return:
		+ True if verify ok
		+ False if verify fail
		+ None if communication error
		"""
		if hashAlgo not in SiriusAPICrypto.dsa_sha_functions:
			print_err("Invalid hash: %s" % hashAlgo)
			return None

		sirius_target = BluefinserialCommand.TARGET_APPLICATION if target == "APP" else BluefinserialCommand.TARGET_RF

		pkt = BluefinserialCommand(sirius_target, verbose=verbose)
		dsa_verify_package = struct.pack('<BBHB',
			1, # operation: verify
			SiriusAPICrypto.dsa_sha_functions[hashAlgo], # sha
			len(message), # message len
			len(signature) # no signature
		) + message + signature

		cmd = pkt.Packet('\x8b', '\x48', dsa_verify_package)
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("Dsa verify fail, code 0x%02x" % ord(rsp[2]))
			return None
		if verbose:
			print("Verify status: %s" % ("ok" if ord(rsp[3]) == 0 else "failed"))
		return True if ord(rsp[3]) == 0 else False

	def Cmac(self, target, cipher, key, message):
		"""
		return:
		CMAC, with corresponding cipher, key, message
		"""
		if cipher not in SiriusAPICrypto.cmac_operation:
			print_err("Invalid cipher: %s" % cipher)
			return None
		if len(key) not in SiriusAPICrypto.cmac_key_length[cipher]:
			print_err("Invalid key length: %d" % len(key))
			return None

		msgLen = len(message)
		sirius_target = BluefinserialCommand.TARGET_APPLICATION if target == "APP" else BluefinserialCommand.TARGET_RF

		pkt = BluefinserialCommand(sirius_target, verbose=False)
		cmac_package = struct.pack('<BBB',
			SiriusAPICrypto.cmac_operation[cipher], # cipher type
			msgLen, # message len
			len(key), # key length
		) + message + key

		cmd = pkt.Packet('\x8b', '\x44', cmac_package)
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("Cmac fail, code 0x%02x" % ord(rsp[2]))
			return None
		return rsp[3:]

	def Aes(self, target, en_dec, mode, iv, key, data):
		"""
		"""
		en_dec = en_dec.upper()
		mode = mode.upper()
		aes_mode = mode + "_" + en_dec
		if aes_mode not in SiriusAPICrypto.aes_mode:
			print_err("Invalid mode: %s" % aes_mode)
			return None
		if len(key) not in SiriusAPICrypto.aes_key_length:
			print_err("Invalid key length: %d" % len(key))
			return None
		if len(data) % SiriusAPICrypto.aes_block_size != 0:
			print_err("Invalid data length: %d" % len(data))
			return None
		if len(iv) != SiriusAPICrypto.aes_block_size:
			print_err("Invalid IV length: %d" % len(iv))
			return None

		numOfBlock = len(data) / SiriusAPICrypto.aes_block_size
		sirius_target = BluefinserialCommand.TARGET_APPLICATION if target == "APP" else BluefinserialCommand.TARGET_RF

		pkt = BluefinserialCommand(sirius_target, verbose=False)
		aes_package = struct.pack('<BB',
			numOfBlock, # number of 16-bytes AES or 8-bytess TDES block
			len(key), # data len
		) + data + key + iv + chr(SiriusAPICrypto.aes_mode[aes_mode])

		cmd = pkt.Packet('\x8b', '\x0c', aes_package)
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("AES fail, code 0x%02x" % ord(rsp[2]))
			return None
		return rsp[3:]

	def Tdes(self, target, en_dec, mode, iv, key, data):
		"""
		"""
		en_dec = en_dec.upper()
		mode = mode.upper()
		tdes_mode = mode + "_" + en_dec
		if tdes_mode not in SiriusAPICrypto.tdes_mode:
			print_err("Invalid mode: %s" % tdes_mode)
			return None
		if len(key) not in SiriusAPICrypto.tdes_key_length:
			print_err("Invalid key length: %d" % len(key))
			return None
		if len(data) % SiriusAPICrypto.tdes_block_size != 0:
			print_err("Invalid data length: %d" % len(data))
			return None
		if len(iv) != SiriusAPICrypto.tdes_block_size:
			print_err("Invalid IV length: %d" % len(iv))
			return None

		numOfBlock = len(data) / SiriusAPICrypto.tdes_block_size
		sirius_target = BluefinserialCommand.TARGET_APPLICATION if target == "APP" else BluefinserialCommand.TARGET_RF

		pkt = BluefinserialCommand(sirius_target, verbose=False)
		tdes_package = struct.pack('<BB',
			numOfBlock, # number of 16-bytes tdes or 8-bytess TDES block
			len(key), # data len
		) + data + key + iv + chr(SiriusAPICrypto.tdes_mode[tdes_mode])

		cmd = pkt.Packet('\x8b', '\x0a', tdes_package)
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("Tdes fail, code 0x%02x" % ord(rsp[2]))
			return None
		return rsp[3:]

	def Rsa(self, target, operation, data, verbose=False):
		"""
		"""
		if operation not in SiriusAPICrypto.rsa_operations:
			print_err("Invalid operation %s" %(operation))
			return None

		sirius_target = BluefinserialCommand.TARGET_APPLICATION if target == "APP" else BluefinserialCommand.TARGET_RF

		pkt = BluefinserialCommand(sirius_target, verbose=verbose)
		rsa_package = struct.pack('<B',
			SiriusAPICrypto.rsa_operations[operation], # rsa operation
		) + data
		cmd = pkt.Packet('\x8b', '\x4c', rsa_package)
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("Rsa %s fail, code 0x%02x" % (operation, ord(rsp[2])))
			return None
		return rsp[3:]

class MlsKeyTlv():
	KeyDict = {
		"DSS_p": 0x01,
		'DSS_q': 0x02,
		'DSS_g': 0x03,
		'DSS_y': 0x04,
		'DSS_x': 0x05,
		'ECDSA_x': 0x06,
		'ECDSA_y': 0x07,
		'ECDSA_pri': 0x08,
		'RSA_n': 0x09,
		'RSA_d': 0x0A,
		'RSA_e': 0x0B,
		'RSA_p': 0x0C,
		'RSA_q': 0x0D,
	}
	VERBOSE = False

	def __init__(self, verbose=False):
		self.valList = []
		self.VERBOSE = verbose

	def AddValList(self, tag, value):
		if tag not in self.KeyDict:
			print_err("Tag %s not regcognize" % tag)
		TL = struct.pack('<BH', self.KeyDict[str(tag)], len(value))
		self.valList.append(TL + value)
		if (self.VERBOSE):
			dump_hex(TL+value, tag + ": ")

	def ValList(self):
		return self.valList

	@staticmethod
	def GetTagVal(tag_name):
		if tag_name not in MlsKeyTlv.KeyDict:
			return None
		return MlsKeyTlv.KeyDict[tag_name]

	@staticmethod
	def GetTagValStr(tag_name):
		if tag_name not in MlsKeyTlv.KeyDict:
			return None
		tag_val_str = struct.pack('<I', MlsKeyTlv.KeyDict[tag_name])
		return tag_val_str
