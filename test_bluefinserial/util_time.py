#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# bootup_check.py


# ---- IMPORTS
import os
import re
import time
import sys
import subprocess
import base64
import md5
import threading
import posix_ipc
import binascii
import struct
from optparse import OptionParser, OptionGroup

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


def print_err(text):
	print >> sys.stderr, bcolors.FAIL + text + bcolors.ENDC

def dump_hex(data, desc_str = ""):
	print desc_str + binascii.hexlify(data)

class crc8:
	def __init__(self):
		self.crcTable = (0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15, 0x38,
				 0x3f, 0x36, 0x31, 0x24, 0x23, 0x2a, 0x2d, 0x70, 0x77,
				 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65, 0x48, 0x4f, 0x46,
				 0x41, 0x54, 0x53, 0x5a, 0x5d, 0xe0, 0xe7, 0xee, 0xe9,
				 0xfc, 0xfb, 0xf2, 0xf5, 0xd8, 0xdf, 0xd6, 0xd1, 0xc4,
				 0xc3, 0xca, 0xcd, 0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b,
				 0x82, 0x85, 0xa8, 0xaf, 0xa6, 0xa1, 0xb4, 0xb3, 0xba,
				 0xbd, 0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2,
				 0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea, 0xb7,
				 0xb0, 0xb9, 0xbe, 0xab, 0xac, 0xa5, 0xa2, 0x8f, 0x88,
				 0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a, 0x27, 0x20, 0x29,
				 0x2e, 0x3b, 0x3c, 0x35, 0x32, 0x1f, 0x18, 0x11, 0x16,
				 0x03, 0x04, 0x0d, 0x0a, 0x57, 0x50, 0x59, 0x5e, 0x4b,
				 0x4c, 0x45, 0x42, 0x6f, 0x68, 0x61, 0x66, 0x73, 0x74,
				 0x7d, 0x7a, 0x89, 0x8e, 0x87, 0x80, 0x95, 0x92, 0x9b,
				 0x9c, 0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4,
				 0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec, 0xc1,
				 0xc6, 0xcf, 0xc8, 0xdd, 0xda, 0xd3, 0xd4, 0x69, 0x6e,
				 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c, 0x51, 0x56, 0x5f,
				 0x58, 0x4d, 0x4a, 0x43, 0x44, 0x19, 0x1e, 0x17, 0x10,
				 0x05, 0x02, 0x0b, 0x0c, 0x21, 0x26, 0x2f, 0x28, 0x3d,
				 0x3a, 0x33, 0x34, 0x4e, 0x49, 0x40, 0x47, 0x52, 0x55,
				 0x5c, 0x5b, 0x76, 0x71, 0x78, 0x7f, 0x6a, 0x6d, 0x64,
				 0x63, 0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b,
				 0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13, 0xae,
				 0xa9, 0xa0, 0xa7, 0xb2, 0xb5, 0xbc, 0xbb, 0x96, 0x91,
				 0x98, 0x9f, 0x8a, 0x8d, 0x84, 0x83, 0xde, 0xd9, 0xd0,
				 0xd7, 0xc2, 0xc5, 0xcc, 0xcb, 0xe6, 0xe1, 0xe8, 0xef,
				 0xfa, 0xfd, 0xf4, 0xf3)

	def crc(self, msg):
		runningCRC = 0
		for c in msg:
			#c = ord(str(c))
			runningCRC = self.crcByte(runningCRC, ord(c))
		return runningCRC

	def crcByte(self, oldCrc, byte):
		res = self.crcTable[oldCrc & 0xFF ^ byte & 0xFF];
		return res

class BluefinserialCommand():
	"""
	Bluefinserial command class
	"""
	pkt = ''
	TARGET_APPLICATION = 0xC5
	TARGET_RF = 0x35
	SURISDK_VERSION = 0x03
	SURIBL_VERSION = 0x02
	PN5180_VERSION = 0x04

	def __init__(self, target):
		"""
		"""
		if target != self.TARGET_RF and target != self.TARGET_APPLICATION:
			print_err("Target is not valid")
			return

		self.target = target
		self.DATA_EXCEPT_CMD = 510
		self.DATA_CMD_MAX_LEN = 512

	def CheckSum(self, data):
		crc = crc8()
		val = crc.crc(data)
		return chr(val)

	def LCS(self, len):
		len_parse = struct.pack('H', len)
		return ord(len_parse[0]) ^ ord(len_parse[1])

	def Packet(self, CmdCode, CtrCode, Data=""):
		# Packet format:
		# FIl        FIm      Lenl        Lenm        LCS         Data        CRC8
		# 0          1         2            3           4         5:x         x+1

		pkt_len = len(Data) + 2
		if pkt_len > self.DATA_CMD_MAX_LEN:
			print_err("Packet build error, packet length too long " + str(pkt_len) + " - maximum: " + str(self.DATA_CMD_MAX_LEN))
			return ""

		self.pkt = struct.pack('<BBHB', 0x00, self.target, pkt_len, self.LCS(pkt_len)) + CmdCode + CtrCode + Data

		# Checksum is calculated from LEN TO END
		self.pkt += self.CheckSum(self.pkt[2:])
		return self.pkt

	def Data(self):
		return self.pkt[4:len(self.pkt)-1]

class BluefinserialSvcRfSession(BluefinserialCommand):
	TIME_WAIT_ACK = 0.5
	TIME_WAIT_RSP = 6
	ACK_RETRY = 3
	VERBOSE = 1

	def __init__(self, target, send_queue, rcv_queue):
		BluefinserialCommand.__init__(self, target)
		self.send_queue = send_queue
		self.rcv_queue = rcv_queue

	def RfPacket(self, CmdCode, CtrCode, Data=""):
		pkt = self.Packet(CmdCode, CtrCode, Data)
		pkt_len = len(pkt)
		pkt_to_queue = struct.pack('<H', pkt_len) + pkt
		return pkt_to_queue

	def FlushRcvQueue(self):
		while True:
			try:
				self.rcv_queue.receive(0.1)
			except posix_ipc.BusyError:
				break

	def ParseQueueData(self, queue_data):
		# Return:
		# 1. error_code (bool: true->success false->fail)
		# 2. response packet
		queue_type, error, frame, rcv_len, len_monitoring, rvc_state = struct.unpack("<II518sIII", queue_data)
		return error, frame, len_monitoring

	def GetACK(self, packet):
		retry = 0
		ret = False
		ACK_PACKET = "\x00\x3A\x00\xff\xff"

		while ret == False and retry < self.ACK_RETRY:
			self.FlushRcvQueue()
			self.send_queue.send(packet)

			try:
				resp, _ = self.rcv_queue.receive(self.TIME_WAIT_ACK)
			except posix_ipc.BusyError:
				# The Target not response ACK, retry
				retry += 1
				continue

			# Check for ACK
			error, rsp, rcv_len = self.ParseQueueData(resp)
			if error != 0:
				retry += 1
				continue
			if (rcv_len != 5) and (rsp[:5] != ACK_PACKET):
				retry += 1
				continue

			# Everything is ok, break and wait for response
			ret = True
		return ret

	def Exchange(self, packet):
		ret = self.GetACK(packet)
		if (ret == False):
			print_err("Not response ACK")
			return None

		raw_queue_resp, _ = self.rcv_queue.receive(self.TIME_WAIT_RSP)
		error, rsp, rcv_len = self.ParseQueueData(raw_queue_resp)
		# Any error, returns
		if error != 0:
			print_err("Send fail")
			return ""

		# Only get the response from target
		response = rsp[5:rcv_len-1]

		# Command code not match, returns
		if response[0] != packet[2+5]:
			print_err("Response's Command code not match, refuse response packet")
			return ""
		# Control code not match, returns
		if ord(response[1]) != (ord(packet[2+6]) + 1):
			print_err("Response's Control code not match, refuse response packet")
			return ""

		return response

	def GetRtc(self):
		cmd = self.RfPacket('\x8b', '\x20', '\x01\x00\x00\x00\x00')
		rsp = self.Exchange(cmd)
		if rsp is None:
			print_err("Error when get RTC from RF processor")
			return

		return ord(rsp[3]) + (ord(rsp[4]) << 8) + (ord(rsp[5]) << 16) + (ord(rsp[6]) << 24)

	def SetRtc(self, set_value):
		cmd_data = struct.pack('<BL', 0x00, set_value)
		cmd = self.RfPacket('\x8b', '\x20', cmd_data)
		rsp = self.Exchange(cmd)
		if rsp is None:
			print_err("Error when set RTC to RF processor")
			return

	def parse_version(self, u32_version):
		firmware_version_rev = u32_version % 100
		firmware_version_minor = ((u32_version - firmware_version_rev) % 10000) / 100
		firmware_version_major = (u32_version - firmware_version_minor - firmware_version_rev) / 10000
		firmware_version_str = str(firmware_version_major) + "." + str(firmware_version_minor) + "." + str(firmware_version_rev)
		return firmware_version_str

	def GetSurisdkVersion(self):
		getVersionPacket = struct.pack('<B', self.SURISDK_VERSION)
		cmd = self.RfPacket('\x8B', '\x00', getVersionPacket)

		rsp = ''
		rsp = self.Exchange(cmd)
		if (rsp is None) or (rsp[2] != '\x00'):
			print_err("Surisdk firmware version check fail")
			return None
		u32_firmware_version = ord(rsp[3]) + (ord(rsp[4]) << 8) + (ord(rsp[5]) << 16)
		firmware_version_str = self.parse_version(u32_firmware_version)
		return firmware_version_str

	def GetSuriblVersion(self):
		getVersionPacket = struct.pack('<B', self.SURIBL_VERSION)
		cmd = self.RfPacket('\x8B', '\x00', getVersionPacket)

		rsp = ''
		rsp = self.Exchange(cmd)
		if (rsp is None) or (rsp[2] != '\x00'):
			print_err("Suribl firmware version check fail")
			return None
		u32_firmware_version = ord(rsp[3]) + (ord(rsp[4]) << 8) + (ord(rsp[5]) << 16)
		firmware_version_str = self.parse_version(u32_firmware_version)
		return firmware_version_str

	def GetPN5180Version(self):
		getVersionPacket = struct.pack('<B', self.PN5180_VERSION)
		cmd = self.RfPacket('\x8B', '\x00', getVersionPacket)

		rsp = ''
		rsp = self.Exchange(cmd)
		if (rsp is None) or (rsp[2] != '\x00'):
			print_err("PN5180 firmware version check fail")
			return None
		u32_firmware_version = ord(rsp[3]) + (ord(rsp[4]) << 8) + (ord(rsp[5]) << 16)
		firmware_version_str = self.parse_version(u32_firmware_version)
		return firmware_version_str

def FlushQueue(queue):
	while True:
		try:
			queue.receive(0.1)
		except posix_ipc.BusyError:
			break

MSQ_QUEUE_RF_SESSION_SEND="/mlsSerialRFEP"
MSQ_QUEUE_RF_SESSION_RECV="/mlsSerialRfCmdSession"

mq_send = posix_ipc.MessageQueue(MSQ_QUEUE_RF_SESSION_SEND)
mq_recv = posix_ipc.MessageQueue(MSQ_QUEUE_RF_SESSION_RECV)

##################################################
# 					Main						 #
##################################################
parser = OptionParser()
parser.add_option(  "-s", "--set",
					dest="set_value",
					type="string",
					help="set RTC value to RF processor")
parser.add_option(  "-g", "--get",
					dest="get_value",
					action="store_true",
					help="get RTC value from RF processor")
parser.add_option(  "-v", "--ver",
					dest="get_version",
					action="store_true",
					help="get version from RF processor")
(options, args) = parser.parse_args()

if options.set_value is None and options.get_value is None and options.get_version is None:
	parser.print_help()
	sys.exit(-1)
if options.set_value and options.get_value:
	parser.print_help()
	sys.exit(-1)


rf_session = BluefinserialSvcRfSession(BluefinserialSvcRfSession.TARGET_RF, mq_send, mq_recv)
if options.set_value:
	rf_session.SetRtc(int(options.set_value))

if options.get_value:
	print rf_session.GetRtc()

if options.get_version:
	print ("SURISDK_VER: %s" % rf_session.GetSurisdkVersion())
	print ("SURIBL_VER:  %s" % rf_session.GetSuriblVersion())
	print ("PN5180_VER:  %s" % rf_session.GetPN5180Version())
