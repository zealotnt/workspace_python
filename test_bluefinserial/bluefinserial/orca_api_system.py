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
import md5

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
	CERT_DOWNLOAD_PACKET_MAX_SIZE = 240

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

	def WriteMultiTLVPacket(self, tag, idx, max_idx, packet_data, debug=False):
		if len(packet_data) > (self.CERT_DOWNLOAD_PACKET_MAX_SIZE * 2):
			raise Exception("Packet data size should be less than " + str(self.CERT_DOWNLOAD_PACKET_MAX_SIZE))

		# Build the packet
		pkt = ""
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF, verbose=debug)
		download_packet = struct.pack('<BBBB', tag, len(packet_data)+2, idx, max_idx) + packet_data
		cmd = pkt.Packet('\x8B', '\x80', download_packet)

		rsp = ''
		rsp = self._datalink.Exchange(cmd)
		if rsp is None:
			print_err("TLV Packet write request fail")
			return None
		sys.stdout.write("Progress: %.2f%%\r" % ((float)(idx)*100.0/(float)(max_idx)))
		sys.stdout.flush()
		return rsp

	def OrcaRfApiUpdateCaCert(self, CA_file, debug=False):
		def GetFileSize(path):
			return os.path.getsize(path)

		def GetNumOfPacket(path):
			file_size = GetFileSize(path)
			if file_size % self.CERT_DOWNLOAD_PACKET_MAX_SIZE == 0:
				return (file_size / self.CERT_DOWNLOAD_PACKET_MAX_SIZE)
			else:
				return ((file_size / self.CERT_DOWNLOAD_PACKET_MAX_SIZE) + 1)

		ca_cmd_tag = MlsInfoTlv.GetTagVal("CA_FILE")
		ca_max_packet = GetNumOfPacket(CA_file)
		ca_contents = GetFileContent(CA_file)
		ca_packet_idx = 0

		while ca_packet_idx <= (ca_max_packet - 1):
			if ca_packet_idx != (ca_max_packet - 1):
				first_idx = ca_packet_idx * self.CERT_DOWNLOAD_PACKET_MAX_SIZE
				end_idx = ((ca_packet_idx + 1) * self.CERT_DOWNLOAD_PACKET_MAX_SIZE)
				ret = self.WriteMultiTLVPacket(ca_cmd_tag,
												ca_packet_idx,
												ca_max_packet-1,
												ca_contents[first_idx:end_idx],
												debug)
			else:
				first_idx = ca_packet_idx * self.CERT_DOWNLOAD_PACKET_MAX_SIZE
				ret = self.WriteMultiTLVPacket(ca_cmd_tag,
												ca_packet_idx,
												ca_max_packet-1,
												ca_contents[first_idx:],
												debug)
			if ret is None:
				print_err("CaCert donwload error")
				return False

			ca_packet_idx += 1

			if debug == True:
				raw_input("Enter to continue with %d: " % (ca_packet_idx))
		# Upgrade successfully
		print_ok("CaCert download successfully")
		return True

	def OrcaRfApiVerifyCaCert(self, CA_file):
		ca_cmd_tag = MlsInfoTlv.GetTagVal("CA_FILE")
		ca_contents = GetFileContent(CA_file)
		ca_md5_hashed = md5.new(ca_contents).digest()
		# Build the packet
		pkt = ""
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		verify_package = struct.pack('<B', ca_cmd_tag)
		cmd = pkt.Packet('\x8B', '\x82', verify_package)

		rsp = ''
		rsp = self._datalink.Exchange(cmd)
		if rsp is None:
			print_err("VerifyCACert request fail")
			return None
		if rsp[2] != '\x00':
			print_err("VerifyCACert request fail, code 0x%02x" % ord(rsp[2]))
			return None

		dump_hex(ca_md5_hashed, "MD5 Hashed file : ")
		dump_hex(rsp[3:], 		"Hash from board : ")
		if ca_md5_hashed == rsp[3:]:
			print_ok("CA File verify OK, files %s are same with cert store in Maxim" % (CA_file))
		return True

	def OrcaRfApiUpdateCaCertFromHeader(self, CA_header_file, array_name, debug=False):
		def GetNumOfPacket(data):
			file_size = len(data)
			if file_size % self.CERT_DOWNLOAD_PACKET_MAX_SIZE == 0:
				return (file_size / self.CERT_DOWNLOAD_PACKET_MAX_SIZE)
			else:
				return ((file_size / self.CERT_DOWNLOAD_PACKET_MAX_SIZE) + 1)

		ca_contents = ParseHeaderFileValue(CA_header_file, array_name)
		ca_cmd_tag = MlsInfoTlv.GetTagVal("CA_FILE")
		ca_max_packet = GetNumOfPacket(ca_contents)
		ca_packet_idx = 0

		while ca_packet_idx <= (ca_max_packet - 1):
			if ca_packet_idx != (ca_max_packet - 1):
				first_idx = ca_packet_idx * self.CERT_DOWNLOAD_PACKET_MAX_SIZE
				end_idx = ((ca_packet_idx + 1) * self.CERT_DOWNLOAD_PACKET_MAX_SIZE)
				ret = self.WriteMultiTLVPacket(ca_cmd_tag,
												ca_packet_idx,
												ca_max_packet-1,
												ca_contents[first_idx:end_idx],
												debug)
			else:
				first_idx = ca_packet_idx * self.CERT_DOWNLOAD_PACKET_MAX_SIZE
				ret = self.WriteMultiTLVPacket(ca_cmd_tag,
												ca_packet_idx,
												ca_max_packet-1,
												ca_contents[first_idx:],
												debug)
			if ret is None:
				print_err("CaCert donwload error")
				return False

			ca_packet_idx += 1

			if debug == True:
				raw_input("Enter to continue with %d: " % (ca_packet_idx))
		# Upgrade successfully
		print_ok("CaCert download successfully")
		return True

	def OrcaRfApiVerifyCaCertFromHeader(self, CA_header_file, array_name):
		ca_cmd_tag = MlsInfoTlv.GetTagVal("CA_FILE")
		data = ParseHeaderFileValue(CA_header_file, array_name)
		ca_md5_hashed = md5.new(data).digest()
		# Build the packet
		pkt = ""
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
		verify_package = struct.pack('<B', ca_cmd_tag)
		cmd = pkt.Packet('\x8B', '\x82', verify_package)

		rsp = ''
		rsp = self._datalink.Exchange(cmd)
		if rsp is None:
			print_err("VerifyCACert request fail")
			return None
		if rsp[2] != '\x00':
			print_err("VerifyCACert request fail, code 0x%02x" % ord(rsp[2]))
			return None

		dump_hex(ca_md5_hashed, "MD5 Hashed file : ")
		dump_hex(rsp[3:], 		"Hash from board : ")
		if ca_md5_hashed == rsp[3:]:
			print_ok("CA File verify OK, files %s are same with cert store in Maxim" % (CA_header_file))
		return True

	def OrcaRfApiUpdateInfo(self, TID=None, MID=None, STAN=None, APN=None, DEV_IP=None, HOST=None, PORT=None):
		info = MlsInfoTlv(verbose=self.VERBOSE)
		if TID is not None:
			info.AddVal('TID', TID)
		if MID is not None:
			info.AddVal('MID', MID)
		if STAN is not None:
			# STAN is stored as 3 bytes big endianess
			STAN_str = struct.pack('>I', STAN)
			STAN_str = STAN_str[1:]
			info.AddVal('STAN', STAN_str)
		if APN is not None:
			info.AddVal('APN', APN)
		if DEV_IP is not None:
			info.AddVal('DEV_IP', DEV_IP)
		if HOST is not None:
			info.AddVal('HOST', HOST)
		if PORT is not None:
			PORT_str = struct.pack('<H', PORT)
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

		print_ok("RfApi UpdateInfo successfully")
		return True

	def OrcaRfApiReadInfo(self, info_str):
		tag = MlsInfoTlv.GetTagValStr(info_str)
		if tag is None:
			print_err("%s not regcognized" % info_str)
		pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF, verbose=self.VERBOSE)
		cmd = pkt.Packet('\x8b', '\x82', tag)
		rsp = self._datalink.Exchange(cmd)
		if (rsp is None):
			print_err("Send fail")
			return None
		if rsp[2] != '\x00':
			print_err("RfApi ReadInfo fail, code 0x%02x" % ord(rsp[2]))
			return None

		print_ok("Read successfully %s: %s" % (info_str, MlsInfoTlv.ParseVal(info_str, rsp[3:])))
		return rsp[3:]

class MlsInfoTlv():
	InfoDict = {
		'TID': 0x02,
		'MID': 0x03,
		'STAN': 0x04,
		'APN': 0x05,
		'HOST': 0x06,
		'PORT': 0x07,
		'DEV_IP': 0x08,
		'CA_FILE': 0x09,
	}
	InfoNumberEndianess = {
		'STAN': "BE",
		'PORT': "LE"
	}
	VERBOSE = False

	def __init__(self, verbose=False):
		self.val = ""
		self.VERBOSE = verbose

	def AddVal(self, tag, value):
		if tag not in self.InfoDict:
			print_err("Tag %s not regcognize" % tag)
		TL = struct.pack('<BB', self.InfoDict[str(tag)], len(value))
		self.val += TL + value
		if (self.VERBOSE):
			dump_hex(TL+value, tag + ": ")

	def Val(self):
		return self.val

	@staticmethod
	def GetTagVal(tag_name):
		if tag_name not in MlsInfoTlv.InfoDict:
			return None
		return MlsInfoTlv.InfoDict[tag_name]

	@staticmethod
	def GetTagValStr(tag_name):
		if tag_name not in MlsInfoTlv.InfoDict:
			return None
		tag_val_str = struct.pack('<I', MlsInfoTlv.InfoDict[tag_name])
		return tag_val_str

	@staticmethod
	def ParseVal(tag_name, value):
		if tag_name not in MlsInfoTlv.InfoDict:
			return None

		string_tags = ['TID', 'MID', 'APN', 'DEV_IP', 'HOST']
		if tag_name in string_tags:
			return value

		number_tags = ['STAN', 'PORT']
		if tag_name in number_tags:
			num_val = 0
			idx = 0
			max_idx = len(value) - 1
			for i in value:
				if MlsInfoTlv.InfoNumberEndianess[tag_name] == "BE":
					# for BE number
					num_val += ord(i) << (8*(max_idx-idx))
				else:
					# for LE number
					num_val += ord(i) << (8*idx)
				idx += 1
			return str(num_val)

		return None

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
