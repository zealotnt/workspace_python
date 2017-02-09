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
class SiriusAPISystem():
	"""
	SiriusAPISystem class, implement system API of Sirius
	"""
	XMSDK_VERSION = 0x73ab
	SVC_VERSION = 0x0500
	SURISDK_VERSION = 0x03
	SURIBL_VERSION = 0x02

	def __init__(self, bluefin_serial):
		"""
		"""
		self._datalink = bluefin_serial

	def parse_version(self, u32_version):
		firmware_version_rev = u32_version % 100
		firmware_version_minor = ((u32_version - firmware_version_rev) % 10000) / 100
		firmware_version_major = (u32_version - firmware_version_minor - firmware_version_rev) / 10000
		firmware_version_str = str(firmware_version_major) + "." + str(firmware_version_minor) + "." + str(firmware_version_rev)
		return firmware_version_str

	def GetXmsdkVersion(self):
		pkt = ""
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_APPLICATION)
		getVersionPacket = struct.pack('<BH', 1, self.XMSDK_VERSION)
		cmd = pkt.Packet('\x10', '\xD2', getVersionPacket)

		rsp = ''
		rsp = self._datalink.Exchange(cmd)
		if rsp is None:
			print_err("Xmsdk firmware version check fail")
			return None
		u32_firmware_version = ord(rsp[5]) + (ord(rsp[6]) << 8) + (ord(rsp[7]) << 16)
		firmware_version_str = self.parse_version(u32_firmware_version)
		print_ok("Xmsdk version: " + str(firmware_version_str))
		print_ok("Xmsdk type %s" % rsp[8])
		return firmware_version_str

	def GetSvcVersion(self):
		pkt = ""
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_APPLICATION)
		getVersionPacket = struct.pack('<BH', 1, self.SVC_VERSION)
		cmd = pkt.Packet('\x10', '\xD2', getVersionPacket)

		rsp = ''
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None) or (rsp[2] != '\x00'):
			print_err("Svc firmware version check fail")
			return None
		u32_firmware_version = ord(rsp[5]) + (ord(rsp[6]) << 8) + (ord(rsp[7]) << 16)
		firmware_version_str = self.parse_version(u32_firmware_version)
		print_ok("Svc version: " + str(firmware_version_str))
		print_ok("Svc type %s" % rsp[8])
		return firmware_version_str

	def GetSurisdkVersion(self):
		pkt = ""
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		getVersionPacket = struct.pack('<B', self.SURISDK_VERSION)
		cmd = pkt.Packet('\x8B', '\x00', getVersionPacket)

		rsp = ''
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None) or (rsp[2] != '\x00'):
			print_err("Surisdk firmware version check fail")
			return None
		u32_firmware_version = ord(rsp[3]) + (ord(rsp[4]) << 8) + (ord(rsp[5]) << 16)
		firmware_version_str = self.parse_version(u32_firmware_version)
		print_ok("Surisdk version: " + str(firmware_version_str))
		return firmware_version_str

	def GetSuriblVersion(self):
		pkt = ""
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		getVersionPacket = struct.pack('<B', self.SURIBL_VERSION)
		cmd = pkt.Packet('\x8B', '\x00', getVersionPacket)

		rsp = ''
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None) or (rsp[2] != '\x00'):
			print_err("Suribl firmware version check fail")
			return None
		u32_firmware_version = ord(rsp[3]) + (ord(rsp[4]) << 8) + (ord(rsp[5]) << 16)
		firmware_version_str = self.parse_version(u32_firmware_version)
		print_ok("Surisdk version: " + str(firmware_version_str))
		return firmware_version_str

	def RfDebugPrintEnable(self):
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		cmd = pkt.Packet('\x8B', '\x24', "\x01\x07")

		rsp = self._datalink.Exchange(cmd)
		if (rsp is None) or (rsp[2] != '\x00'):
			print_err("RfDebugPrintEnable command fail")
			return None
		return True

	def SetRootPassword(self, password=""):
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_APPLICATION)
		# always has null character at the end
		set_password_package = struct.pack('<BB', 4, len(password)) + password
		cmd = pkt.Packet('\x20', '\x10', set_password_package)

		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("SetRootPassword execute fail, code 0x%02x" % ord(rsp[2]))
			return None

		print_ok("Set root password to '%s' successfully" % password)
		return True

	def RfApiVerifyPassword(self, password):
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		# always has null character at the end
		cmd = pkt.Packet('\x8b', '\x74', password)

		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("RfApi Verify password  fail, code 0x%02x" % ord(rsp[2]))
			return None

		print_ok("Verify password successfully")
		return True

	def RfApiUpdatePassword(self, old_password, new_password):
		if self.RfApiVerifyPassword(old_password) is None:
			return None

		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		# always has null character at the end
		cmd = pkt.Packet('\x8b', '\x76', new_password)

		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("RfApi Update password fail, code 0x%02x" % ord(rsp[2]))
			return None

		print_ok("RfApi Set password to '%s' successfully" % new_password)
		return True
