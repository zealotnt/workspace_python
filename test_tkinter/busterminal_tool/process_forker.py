#!/usr/bin/env python

# ---- IMPORTS
import os
import re
import time
import sys
import subprocess
import json
import base64
import md5
import serial
import thread
import inspect

_port = serial.Serial(port="/dev/ttyGS0", baudrate=9600, timeout=0.1)

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
SCRIPT = "/home/root/script.sh"

def RunApplication(command):
	return subprocess.Popen([SCRIPT, command],
							stdin=subprocess.PIPE,
							stdout=subprocess.PIPE,
							stderr=subprocess.PIPE)

def GetApplicationName(argument):
	result = re.findall(r'/(\w+)[\s\r\n$]', argument)
	if len(result) == 0:
		result = re.findall(r'/(\w+)$', argument)
		return result[0]
	return result[0]

class SerialSession():
	def __init__(self):
		self.running = False

	def StopSerialSession(self):
		if self.running == True:
			print "just kill" + self._last_application
			# self.pSsh.terminate()
			# self.pSsh.kill()
			self.running = False
			os.system("killall " + self._last_application)

	def CallSshScript(self, argument):
		if argument == "":
			return
		self.running = True
		self.pSsh = RunApplication(argument)
		self._last_application = GetApplicationName(self.app_name)
		print "Just start app = " + self._last_application
		output, err = self.pSsh.communicate()
		print "App just end !!! with output: "
		print output

	def CreateSerialSession(self, argument, app_name):
		print "Calling: " + app_name
		self.app_name = app_name
		thread.start_new_thread(self.CallSshScript, (argument, ))

forker = SerialSession()
packet = ""
while True:
	waiting = _port.inWaiting()
	read_bytes = _port.read(1 if waiting == 0 else waiting)
	packet += read_bytes

	if "\r" in read_bytes:
		forker.StopSerialSession()
		forker.CreateSerialSession(packet, packet)
		packet = ""