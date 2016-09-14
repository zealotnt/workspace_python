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

PACKET_MAX_SIZE = 480

def GetFileSize(path):
	return os.path.getsize(path)

def GetNumOfPacket(path):
	file_size = GetFileSize(path)
	if file_size % PACKET_MAX_SIZE == 0:
		return (file_size / PACKET_MAX_SIZE)
	else:
		return ((file_size / PACKET_MAX_SIZE) + 1)

#---- CLASSES
class SiriusAPIFwUpgrade():
	"""
	SiriusAPIFwUpgrade class, implement firmware upgrade API of Sirius
	"""
	def __init__(self, bluefin_serial):
		"""
		"""
		self._datalink = bluefin_serial

	def WriteFirmwarePacket(self, paramId, numOfPacket, packet_number, remain_packet, packet_len, packet_data):
		if packet_len > PACKET_MAX_SIZE:
			raise Exception("Packet len should be less than " + str(PACKET_MAX_SIZE))
		if len(packet_data) > (PACKET_MAX_SIZE * 2):
			raise Exception("Packet data size should be less than " + str(PACKET_MAX_SIZE))
		if remain_packet <= 0:
			remain_packet = 0

		# Build the packet
		pkt = ""
		pkt = BluefinserialCommand(0xC5)
		download_packet = struct.pack('<HHHHH', paramId, numOfPacket, packet_number, remain_packet, packet_len) + packet_data
		cmd = pkt.Packet('\x10', '\xD0', download_packet)

		rsp = ''
		rsp = self._datalink.Exchange(cmd)
		if rsp is None:
			print_err("Firmware write request fail")
			return None
		sys.stdout.write("Progress: %.2f%%\r" % ((float)(packet_number)*100.0/(float)(numOfPacket)))
		sys.stdout.flush()
		return rsp

	def DownloadFirmware(self, paramId, file_path):
		fw = open(file_path, "rb")
		fw_max_packet = GetNumOfPacket(file_path)
		fw_contents = GetFileContent(file_path)
		fw_idx = 0

		numOfPacket = fw_max_packet
		remain_packet = 0

		while fw_idx <= (fw_max_packet - 1):
			if fw_idx != (fw_max_packet - 1):
				first_idx = fw_idx * PACKET_MAX_SIZE
				end_idx = ((fw_idx + 1) * PACKET_MAX_SIZE)
				ret = self.WriteFirmwarePacket(paramId,
												numOfPacket,
												fw_idx,
												numOfPacket - fw_idx - 1,
												PACKET_MAX_SIZE,
												fw_contents[first_idx:end_idx])
			else:
				first_idx = fw_idx * PACKET_MAX_SIZE
				ret = self.WriteFirmwarePacket(paramId,
												numOfPacket,
												fw_idx,
												numOfPacket - fw_idx - 1,
												len(fw_contents[first_idx:]),
												fw_contents[first_idx:])
			if ret is None:
				print_err("Firmware donwload error")
				return False

			fw_idx += 1
		# Upgrade successfully
		print_ok("Firmware download successfully")
		return True

	def BeginUpgrade(self, paramId):
		# Build the packet
		pkt = ""
		pkt = BluefinserialCommand(0xC5)
		cmd = pkt.Packet('\x10', '\x60', chr(paramId))

		rsp = ''
		rsp = self._datalink.Exchange(cmd)
		if rsp is None:
			print_err("Firmware request execute fail")
			return False
		if len(rsp) < 3:
			return False
		if rsp[2] != 0:
			return False

		return True

	def PollForStatus(self, paramId):
		# Build the packet
		pkt = ""
		pkt = BluefinserialCommand(0xC5)
		cmd = pkt.Packet('\x10', '\x64', chr(paramId) + '\x00')

		while True:
			time.sleep(1)
			rsp = ''
			rsp = self._datalink.Exchange(cmd)
			if rsp is None:
				print_err("Firmware request execute fail")
				return False
			if len(rsp) < 3:
				return False

			if rsp[2] == '\x00':
				return True

	def UpgradeFirmware(self, firmware_type, file_path):
		time_start = float(time.time() * 1000)

		paramId = 0
		if firmware_type == "rf_fw":
			paramId = 0x06
		elif firmware_type == "rf_bl":
			paramId = 0x07
		elif firmware_type == "app_fw":
			paramId = 0x73
		elif firmware_type == "app_svc":
			paramId = 0x05
		else:
			print_err("Invalid firmware_type")
			return

		ret = self.DownloadFirmware(paramId, file_path)
		if ret is False:
			return False

		ret = self.BeginUpgrade(paramId)
		ret = self.PollForStatus(paramId)
		if ret is False:
			return False

		time_end = float(time.time() * 1000)
		print_ok("Download tooks " + str((time_end - time_start)/1000) + " s")
		return True
