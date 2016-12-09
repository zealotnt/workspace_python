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
class ExampleAPDU():
	SECURE_MEM_APDU_1 = "\x00\xa4\x04\x00\x07\xa0\x00\x00\x01\x51\x00\x00"

class PPSBaudrate():
	B9600 = '\x00'
	B19200 = '\x01'
	B38400 = '\x02'
	B76800 = '\x03'
	B115200 = '\x04'
	B230400 = '\x05'
	B409600 = '\x06'

class SiriusAPISam():
	"""
	SiriusAPISam class, implement SAM API of Sirius
	"""
	MAX_SAM_SLOT = 8

	def __init__(self, bluefin_serial):
		"""
		"""
		self._datalink = bluefin_serial

	def ActivateSam(self, slot):
		if slot > self.MAX_SAM_SLOT:
			print_err("SAM slot invalid, please input SAM slot <= " + str(self.MAX_SAM_SLOT))
			return ""

		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		cmd = pkt.Packet('\x89', '\x02', chr(slot))

		rsp = self._datalink.Exchange(cmd)
		if rsp is None:
			print_err("Send Activate SAM command fail")
			return None

		if rsp[2] != '\x00':
			print_err("Activate SAM fail")
			return None
		if (ord(rsp[3]) + 4) != len(rsp):
			print_err("Invalid SAM Activate API response")
			return None

		dump_hex(rsp[4:len(rsp)], "SAM %d ATR = " % (slot))
		return rsp[4:len(rsp)]

	def DeactivateSam(self, slot):
		if slot > self.MAX_SAM_SLOT:
			print_err("SAM slot invalid, please input SAM slot <= " + str(self.MAX_SAM_SLOT))
			return ""

		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		cmd = pkt.Packet('\x89', '\x08', chr(slot))

		rsp = self._datalink.Exchange(cmd)
		if rsp is None:
			print_err("Send deactivate SAM command fail")
			return None

		if rsp[2] != '\x00':
			print_err("Deactivate SAM fail")
			return None
		return True

	def PpsSam(self, slot, baudrate):
		if slot > self.MAX_SAM_SLOT:
			print_err("SAM slot invalid, please input SAM slot <= " + str(self.MAX_SAM_SLOT))
			return ""

		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		# Format:
		# 0x89 0x04 slot baudrate atrlen [atr]
		cmd = pkt.Packet('\x89', '\x04', chr(slot) + baudrate + '\x00')

		rsp = self._datalink.Exchange(cmd)
		if rsp is None:
			print_err("Send pps SAM command fail")
			return None

		if rsp[2] != '\x00':
			print_err("Pps SAM fail")
			return None
		return True

	def ExchangeAPDU(self, slot, apdu):
		if slot > self.MAX_SAM_SLOT:
			print_err("SAM slot invalid, please input SAM slot <= " + str(self.MAX_SAM_SLOT))
			return ""

		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		apdu_packet = struct.pack('<BH', slot, len(apdu)) + apdu
		cmd = pkt.Packet('\x89', '\x06', apdu_packet)

		rsp = self._datalink.Exchange(cmd)
		if rsp is None:
			print_err("Exchange SAM APDU command fail, no response")
			return None

		if rsp[2] != '\x00':
			print_err("Exchange SAM APDU fail")
			return None
		if (ord(rsp[3]) + ord(rsp[4]) + 5) != len(rsp):
			print_err("Invalid SAM Exchange APDU API response")
			return None

		dump_hex(rsp[5:len(rsp)], "SAM %d R-APDU = " % (slot))
		return rsp[5:len(rsp)]
