#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# sirius_api_fw_upgrade.py
# [CRC32 online tool](http://www.sunshine2k.de/coding/javascript/crc/crc_js.html)

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

#---- CLASSES
class OrcaAPISystem():
	"""
	SiriusAPISystem class, implement system API of Sirius
	"""
	XMSDK_VERSION = 0x73ab
	SVC_VERSION = 0x0500
	SURISDK_VERSION = 0x03
	SURIBL_VERSION = 0x02
	VERBOSE=False

	def __init__(self, bluefin_serial, verbose=False):
		"""
		"""
		self._datalink = bluefin_serial
		self.VERBOSE = verbose

	def OrcaRfApiSetBuzzer(self, freq_val):
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF, verbose=self.VERBOSE)
		freq_val_str = struct.pack('<H', freq_val)
		cmd = pkt.Packet('\x8b', '\x1E', freq_val_str)

		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("Set buzzer fail, code 0x%02x" % ord(rsp[2]))
			return None

		print_ok("Set buzzer successfully")
		return True

	def OrcaRfApiSetLed(self, led_val):
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF, verbose=self.VERBOSE)
		led_val_str = struct.pack('<B', led_val)
		cmd = pkt.Packet('\x8b', '\x1E', led_val_str)

		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("Set led fail, code 0x%02x" % ord(rsp[2]))
			return None

		print_ok("Set led successfully")
		return True

	def OrcaRfApiVerifyPassword(self, password):
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF, verbose=self.VERBOSE)
		verify_password_package = struct.pack('<BB', len(password), 0) + password
		cmd = pkt.Packet('\x8b', '\x74', verify_password_package)

		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("RfApi Verify password  fail, code 0x%02x" % ord(rsp[2]))
			return None

		print_ok("Verify password successfully")
		return True

	def OrcaRfApiUpdatePassword(self, old_password, new_password):
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF, verbose=self.VERBOSE)
		verify_password_package = struct.pack('<BB', len(old_password), len(new_password)) + old_password + new_password
		cmd = pkt.Packet('\x8b', '\x74', verify_password_package)

		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("RfApi Update password fail, code 0x%02x" % ord(rsp[2]))
			return None

		print_ok("RfApi Set password to '%s' successfully" % new_password)
		return True

	def OrcaRfApiUpdateInfo(self, TID=None, MID=None, STAN=None, APN=None, HOST=None, PORT=None):
		info = MlsInfoTlv()
		if TID is not None:
			info.AddVal('TID', TID)
		if MID is not None:
			info.AddVal('MID', MID)
		if STAN is not None:
			STAN_str = struct.pack('<I', STAN)
			STAN_str = STAN_str[:len(STAN_str)-1]
			info.AddVal('STAN', STAN_str)
		if APN is not None:
			info.AddVal('APN', APN)
		if HOST is not None:
			info.AddVal('HOST', HOST)
		if PORT is not None:
			PORT_str = struct.pack('<I', PORT)
			info.AddVal('PORT', PORT_str)

		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF, verbose=self.VERBOSE)
		cmd = pkt.Packet('\x8b', '\x80', info.Val())
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("RfApi UpdateInfo fail, code 0x%02x" % ord(rsp[2]))
			return None

		return True

class MlsInfoTlv():
	InfoDict = {
		'TID': 0x02,
		'MID': 0x03,
		'STAN': 0x04,
		'APN': 0x05,
		'HOST': 0x06,
		'PORT': 0x07,
	}
	def __init__(self):
		self.val = ""

	def AddVal(self, tag, value):
		if tag not in self.InfoDict:
			print_err("Tag %s not regcognize" % tag)
		TL = struct.pack('<BB', self.InfoDict[str(tag)], len(value))
		self.val += TL + value
		dump_hex(TL+value, tag + ": ")

	def Val(self):
		return self.val

class MlsOrcaLeds():
	BLUE=0x01
	ORANGE=0x02
	GREEN=0x04
	RED=0x08

	@staticmethod
	def ParseString(value=""):
		val = 0
		value = value.upper()
		if "B" in value:
			val += MlsOrcaLeds.BLUE
		if "O" in value:
			val += MlsOrcaLeds.ORANGE
		if "G" in value:
			val += MlsOrcaLeds.GREEN
		if "R" in value:
			val += MlsOrcaLeds.RED
		return val
