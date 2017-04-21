#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-04-21 08:58:24

import os
import re
import time
import sys
import serial
import struct
import inspect
from optparse import OptionParser, OptionGroup

# [Ref](http://stackoverflow.com/questions/5067604/determine-function-name-from-within-that-function-without-using-traceback)
MYNAME = lambda: inspect.stack()[1][3]

class MardownTableGenerator():
	def __init__(self):
		self.text = ""
		self.init = False

	def CreateTable(self, listColumn):
		if not type(listColumn) is list:
			print("%s(), listColumn is not a list" % MYNAME())
			return None

		for column in listColumn:
			self.text += "| %s " % column
		self.text += "|\r\n"
		self.init = True
		return True

	def AddRow(self, listColumn):
		if self.init != True:
			print("%s(), table is not created yet" % MYNAME())
			return None

		for column in listColumn:
			self.text += "| %s " % column
		self.text += "|\r\n"
		return True

	def Table(self):
		if self.init != True:
			print("%s(), table is not created yet" % MYNAME())
			return None
		return self.text

class ResultParser():
	@staticmethod
	def DictModel():
		return {
			"Method": "",
			"BlockSize": "",
			"KeySize": "",
			"TimeRunning": "",
			"ActualTime": "",
			"ResultTimes": ""
		}

	@staticmethod
	def ParseNonPublicResult(content):
		# Some non-public key cryptography parser
		#                           #0       #1      #2                 #3   #4          #5
		match = re.findall(r'Doing (.+) for (.+) on (.+) size blocks: (\d+) (.+)\'s in ([\d.]+)s', content)
		resultList = []
		for item in match:
			convertedDict = ResultParser.DictModel()
			method = item[0]
			timeRunning = item[1]
			blockSize = item[2]
			resultTimes = item[3]
			method_2nd = item[4]
			actualTime = item[5]
			if method != method_2nd:
				print ("method != method_2nd, something error !!!")
				continue
			# print(method, blockSize, timeRunning, resultTimes, actualTime)
			convertedDict["Method"] = method
			convertedDict["BlockSize"] = blockSize
			convertedDict["TimeRunning"] = timeRunning
			convertedDict["ActualTime"] = actualTime
			convertedDict["ResultTimes"] = resultTimes
			resultList.append(convertedDict)
		return resultList

	@staticmethod
	def ParsePublicResult(content):
		# Parse the public key cryptography result
		#                           #0        #1           #2      #3   #4       #5         $6
		match = re.findall(r'Doing (\d+) bit (.+)\'s for (\d+)s: (\d+) (\d+) bit (.+) in ([\d\.]+)s', content)
		resultList = []
		for item in match:
			convertedDict = ResultParser.DictModel()
			keySize = item[0]
			method = item[1]
			timeRunning = item[2]
			resultTimes = item[3]
			keySize_2nd = item[4]
			method_2nd = item[5]
			actualTime = item[6]
			if keySize != keySize_2nd:
				print("keySize != keySize_2nd, something error !!!")
				continue
			# print(method, keySize, timeRunning, resultTimes, actualTime)
			convertedDict["Method"] = method
			convertedDict["KeySize"] = keySize
			convertedDict["TimeRunning"] = timeRunning
			convertedDict["ActualTime"] = actualTime
			convertedDict["ResultTimes"] = resultTimes
			resultList.append(convertedDict)
		return resultList

	@staticmethod
	def ParseECDHResult(content):
		# Parse the ECDH
		#                           #0         #1          #2      #3    #4        #5           #6
		match = re.findall(r'Doing (\d+) bit  (.+)\'s for (\d+)s: (\d+) (\d+)-bit (.+) ops in ([\d\.]+)s', content)
		resultList = []
		for item in match:
			convertedDict = ResultParser.DictModel()
			keySize = item[0]
			method = item[1]
			timeRunning = item[2]
			resultTimes = item[3]
			keySize_2nd = item[4]
			method_2nd = item[5]
			actualTime = item[6]
			if keySize != keySize_2nd:
				print ("keySize != keySize_2nd, something error")
				continue
			if method.upper() != method_2nd.upper():
				print ("method.upper() != method_2nd.upper(), something error")
				continue
			# print(method, keySize, timeRunning, resultTimes, actualTime)
			convertedDict["Method"] = method
			convertedDict["KeySize"] = keySize
			convertedDict["TimeRunning"] = timeRunning
			convertedDict["ActualTime"] = actualTime
			convertedDict["ResultTimes"] = resultTimes
			resultList.append(convertedDict)
		return resultList

def _demoUsage(fileContent):
	listResult = ResultParser.ParseNonPublicResult(fileContent)
	nonPublicTableLayout = ["Method", "Block size", "Time running", "Actual time", "Time completed"]
	nonPublicTable = MardownTableGenerator()
	nonPublicTable.CreateTable(nonPublicTableLayout)
	for item in listResult:
		nonPublicTableRow = [item["Method"], item["BlockSize"], item["TimeRunning"], item["ActualTime"], item["ResultTimes"]]
		nonPublicTable.AddRow(nonPublicTableRow)
	# print(nonPublicTable.Table())

	listResult = ResultParser.ParsePublicResult(fileContent)
	publicTableLayout = ["Method", "Key size", "Time running", "Actual time", "Time completed"]
	publicTable = MardownTableGenerator()
	publicTable.CreateTable(publicTableLayout)
	for item in listResult:
		publicTableRow = [item["Method"], item["KeySize"], item["TimeRunning"], item["ActualTime"], item["ResultTimes"]]
		publicTable.AddRow(publicTableRow)
	# print(publicTable.Table())

	listResult = ResultParser.ParseECDHResult(fileContent)
	ecdhTableLayout = ["Method", "Key size", "Time running", "Actual time", "Time completed"]
	ecdhTable = MardownTableGenerator()
	ecdhTable.CreateTable(ecdhTableLayout)
	for item in listResult:
		ecdhTableRow = [item["Method"], item["KeySize"], item["TimeRunning"], item["ActualTime"], item["ResultTimes"]]
		ecdhTable.AddRow(ecdhTableRow)
	# print(ecdhTable.Table())

def main():
	parser = OptionParser()

	parser.add_option(  "-f", "--file",
						dest="filePath",
						type="string",
						default="",
						help="point to path of result file to parse")
	(options, args) = parser.parse_args()

	# Strip of file:// if any
	fileProtocolPrefix = "file:///"
	file = options.filePath
	if file.startswith(fileProtocolPrefix):
		file = file[len(fileProtocolPrefix)-1:]

	# Check file is invalid
	if file == "":
		print("Please specify file path with flag -f or --file")
		sys.exit(1)

	if not os.path.isfile(file):
		print("File path %s not found" % (file))
		sys.exit(1)

	# Open and read the file
	f = open(file, 'rb')
	fileContent = f.read()


if __name__ == "__main__":
	main()
