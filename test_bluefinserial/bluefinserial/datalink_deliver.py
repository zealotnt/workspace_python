#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# datalink_deliver.py
# [Python Serial Ref](https://pythonhosted.org/pyserial/pyserial_api.html)
# [Python binascii Ref](https://docs.python.org/2/library/binascii.html)
# [Python struct Ref](https://docs.python.org/3/library/struct.html)
# [Python struct TUT](https://pymotw.com/2/struct/)
# [Python builtin function Ref](https://docs.python.org/2/library/functions.html)
# [Python string Ref](http://thepythonguru.com/python-strings/)


#---- IMPORTS
import serial
import struct
import binascii
import time

from crc8 import crc8
from utils import *

#---- CONSTANT
BLUEFINSERIAL_BAUDRATE = 115200
BLUEFINSERIAL_DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"

#---- CLASSES

class BluefinserialCommand():
	"""
	Bluefinserial command class
	"""
	pkt = ''
	def __init__(self):
		"""
		"""
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

		self.pkt = struct.pack('<BBHB', 0x00, 0x35, pkt_len, self.LCS(pkt_len)) + CmdCode + CtrCode + Data

		# Checksum is calculated from LEN TO END
		self.pkt += self.CheckSum(self.pkt[2:])
		return self.pkt

	def Data(self):
		return self.pkt[4:len(self.pkt)-1]


class BluefinserialSend():
	"""
	BluefinserialSend extends `Serial` by adding functions to read BluefinSerial commands.
	"""
	FLUSH_INPUT = 100
	ACK_RETRY = 3
	ACK_TIMEOUT = 500
	RESPONSE_TIMEOUT = 6000
	NACK_PACKET = '\x00\x35\x01\xff\xfe'
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

	def WaitTillFinishRcv(self):
		time_start = float(time.time() * 1000)
		while True:
			time_check = float(time.time() * 1000)
			waiting = self._port.inWaiting()
			read_bytes = self._port.read(1 if waiting == 0 else waiting)
			if read_bytes == '' and (time_check - time_start) > self.FLUSH_INPUT:
				self._port.flushInput()
				return

	def Exchange(self, packet):
		self._ack_remain = ""
		self._response = ""
		self._full_packet = ""

		retry = 0
		ret = False
		while ret == False and retry < self.ACK_RETRY:
			self._port.write(packet)
			ret = self.GetACK()
			if ret is False:
				# If fail, flush all input
				self.WaitTillFinishRcv()
				print_err("ACK not received, retry " + str(retry + 1))
			else:
				# If ok, quit while loop, without increase retry counter
				break
			retry += 1

		# If receive ACK fail, return
		if ret == False or retry >= self.ACK_RETRY:
			print_err("Send fail after retry 3 times")
			return None

		# Get respone packet
		ret = self.GetResponse(self._ack_remain)

		# If receive ACK, but not receive Response successfully,
		# send NACK, then wait for try-again-response paket
		if ret == False:
			retry = 0
			while ret == False and retry < self.ACK_RETRY:
				self.WaitTillFinishRcv()
				self._port.write(self.NACK_PACKET)
				ret = self.GetResponse("")
				if ret is False:
					# If fail, flush all input
					self.WaitTillFinishRcv()
					print_err("Response not received, send NACK and retry " + str(retry + 1))
				else:
					# If ok, quit while loop, without increase retry counter
					break
				retry += 1

		if ret == False or retry >= self.ACK_RETRY:
			print_err("Receive response fail")
			return None
		if self._response[0] != packet[5]:
			print_err("Response's Command code not match, refuse response packet")
			return None
		if ord(self._response[1]) != (ord(packet[6]) + 1):
			if (self._response[0] == '\xFF'):
				print_err("Response's Command code not match, the command may is not supported, refuse response packet")
			elif (self._response[1] == '\x7F'):
				print_err("Response's Command code not match, the command may is not supported, refuse response packet")
			else:
				print_err("Not regconize response, refuse response packet")
			return None
		return self._response

	def GetACK(self):
		partial_packet = ""
		ACK_PACKET = "\x00\x3a\x00\xff\xff"
		time_start = float(time.time() * 1000)
		while True:
			time_check = float(time.time() * 1000)
			waiting = self._port.inWaiting()
			read_bytes = self._port.read(1 if waiting == 0 else waiting)
			if read_bytes == '' and (time_check - time_start) > self.ACK_TIMEOUT :
				if len(partial_packet) != 0:
					print_err_dump(partial_packet, "ACK read timeout, rcv before timeout: ")
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
					print_err_dump(partial_packet, "Not expected ACK packet")
					return False

	def GetResponse(self, remain):
		partial_packet = remain
		pkt_len = 0
		FI_HDR = "\x00\x3a"
		STATE = 0
		pkt_frame_len = ""
		pkt_frame_data = ""
		loop_times = 0
		time_start = float(time.time() * 1000)
		while True:
			time_check = float(time.time() * 1000)

			if (len(partial_packet) >= 2 and
				STATE == 0):
				if FI_HDR == partial_packet[:2]:
					STATE = 1
					partial_packet = partial_packet[2:]
				else:
					print_err_dump(partial_packet, "Wrong Rsp header, return")
					return False
			if (len(partial_packet) >= 3 and
				STATE == 1):
				if ((ord(partial_packet[0]) ^ ord(partial_packet[1])) != ord(partial_packet[2])):
					print_err_dump(partial_packet, "LCS not equal Lm ^ Ll, return")
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
					print_err_dump(partial_packet, "Wrong CRC8 checksum")
					return False
				self._response = pkt_frame_data
				return True

			waiting = self._port.inWaiting()
			read_bytes = self._port.read(1 if waiting == 0 else waiting)

			if read_bytes == '' and (time_check - time_start) > self.RESPONSE_TIMEOUT:
				print_err_dump(self._full_packet, "Receive timeout, receive: ")
				return False

			for b in read_bytes:
				self._full_packet += b
				partial_packet += b


