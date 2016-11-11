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

		pkt = ""
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		cmd = pkt.Packet('\x89', '\x02', chr(slot))

		rsp = ''
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

		dump_hex(rsp[4:len(rsp)-1], "SAM " + str(slot) + " ATR = ")
		return rsp[4:len(rsp)-1]

	def ExchangeAPDU(self, apdu):
		if slot > self.MAX_SAM_SLOT:
			print_err("SAM slot invalid, please input SAM slot <= " + str(self.MAX_SAM_SLOT))
			return ""

		pkt = ""
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		apdu_packet = struct.pack('<BH', slot, len(apdu)) + apdu
		cmd = pkt.Packet('\x89', '\x06', apdu_packet)

		rsp = ''
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

		dump_hex(rsp, "Rcv " + len(rsp) " bytes")
		dump_hex(rsp[5:len(rsp)-1], "SAM " + str(slot) + " R-APDU = ")
		return rsp[5:len(rsp)-1]