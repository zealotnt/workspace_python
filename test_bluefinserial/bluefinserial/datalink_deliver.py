#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# datalink_deliver.py


#---- IMPORTS
import serial
import struct
import binascii
import time

from crc8 import crc8
from utils import *

class BluefinserialCommand():
	"""
	Bluefinserial command class
	"""
	pkt = ''
	def __init__(self):
		"""
		"""
		
	def CheckSum(self, data):
		crc = crc8()
		val = crc.crc(data)
		return chr(val)

	def LCS(self, len):
		len_parse = struct.pack('H', len)
		return ord(len_parse[0]) ^ ord(len_parse[1])

	def Packet(self, CmdCode, CtrCode, Data):
		# Packet format:
		# FIl        FIm      Lenl        Lenm        LCS         Data        CRC8
		# 0          1         2            3           4         5:x         x+1

		pkt_len = len(Data) + 2
		self.pkt = struct.pack('<BBHB', 0x00, 0x35, pkt_len, self.LCS(pkt_len)) + CmdCode + CtrCode + Data
		
		# Checksum is calculated from LEN TO END
		self.pkt += self.CheckSum(self.pkt[2:])
		return self.pkt

	def Data(self):
		return self.pkt[4:len(self.pkt)-1]


class BluefinserialSend(serial.Serial):
	"""
	BluefinserialSend extends `Serial` by adding functions to read BluefinSerial commands.
	"""
	ACK_RETRY = 3
	ACK_TIMEOUT = 500
	RESPONSE_TIMEOUT = 6000
	def __init__(self, port, baud):
		"""
		:Parameter port: serial port to use (/dev/tty* or COM*)
		"""
		# worst-case latency timer should be 100ms (actually 20ms)
		self._timeout = 0.1
		self.__full_packet = ""
		self._response = ""
		self._ack_remain = ""
		self._port = serial.Serial(port=port, baudrate=baud, timeout=self._timeout)
		
	def Exchange(self, packet):
		retry = 0
		self._ack_remain = ""
		self._response = ""
		self._full_packet = ""

		self._port.flushInput()
		self._port.write(packet)

		ret = self.GetACK()
		if ret is False:
			print_err("ACK not received, retry " + str(retry))
			return None

		ret = self.GetResponse(self._ack_remain)

		if ret == False:
			return None

		return self._response

	def GetACK(self):
		partial_packet = ""
		ACK_PACKET = "\x00\x3a\x00\xff\xff"
		time_start = int(round(time.time() * 1000))
		while True:
			time_check = int(round(time.time() * 1000))
			waiting = self._port.inWaiting()
			read_bytes = self._port.read(1 if waiting == 0 else waiting)
			if read_bytes == '' and (time_check - time_start) > self.ACK_TIMEOUT :
				if len(partial_packet) != 0:
					dump_hex(partial_packet, "ACK read timeout, rcv before timeout: ")
				return False

			for b in read_bytes:
				self._full_packet += b
				partial_packet += b

			if len(partial_packet) >= 5:
				if ACK_PACKET == partial_packet[:5]:
					partial_packet = partial_packet[5:]
					self._ack_remain = partial_packet
					return True
				else:
					print_err("Not expected ACK packet")
					return False

	def GetResponse(self, remain):
		partial_packet = remain
		pkt_len = 0
		FI_HDR = "\x00\x3a"
		STATE = 0
		pkt_frame_len = ""
		pkt_frame_data = ""
		loop_times = 0
		time_start = int(round(time.time() * 1000))
		while True:
			time_check = int(round(time.time() * 1000))

			if (len(partial_packet) >= 2 and 
				STATE == 0):
				if FI_HDR == partial_packet[:2]:
					STATE = 1
					partial_packet = partial_packet[2:]
				else:
					print_err("Wrong Rsp header, return")
					return False
			if (len(partial_packet) >= 3 and 
				STATE == 1):
				if ((ord(partial_packet[0]) ^ ord(partial_packet[1])) != ord(partial_packet[2])):
					dump_hex(partial_packet)
					print_err("LCS not equal Lm ^ Ll, return")
					return False
				pkt_len = ord(partial_packet[0]) + ord(partial_packet[1])*256
				pkt_frame_len = partial_packet[:3]
				partial_packet = partial_packet[3:]
				STATE = 2
			if (len(partial_packet) >= pkt_len and 
				STATE == 2):
				pkt_frame_data = partial_packet[:pkt_len]
				STATE = 3
			if (len(partial_packet) == (pkt_len + 1) and 
				STATE == 3):
				crc = crc8()
				val = crc.crc(pkt_frame_len + pkt_frame_data)
				if chr(val) != partial_packet[len(pkt_frame_data)]:
					print_err("Wrong CRC8 checksum")
					return False
				self.response = pkt_frame_data	
				return True
			
			waiting = self._port.inWaiting()
			read_bytes = self._port.read(1 if waiting == 0 else waiting)

			if read_bytes == '' and (time_check - time_start) > self.RESPONSE_TIMEOUT:
				dump_hex(self._full_packet, "Receive timeout, receive: ")
				return False

			for b in read_bytes:
				self._full_packet += b
				partial_packet += b


