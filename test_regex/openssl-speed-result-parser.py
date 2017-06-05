#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-04-21 08:58:24

import os
import re
import time
import sys
import inspect
from optparse import OptionParser, OptionGroup

# [Ref](http://stackoverflow.com/questions/5067604/determine-function-name-from-within-that-function-without-using-traceback)
MYNAME = lambda: inspect.stack()[1][3]
ENDLINE = "\r\n"

class MardownTableGenerator():
	def __init__(self):
		self.text = ""
		self.init = False

	def CreateTable(self, listColumn):
		if not type(listColumn) is list:
			print("%s(), listColumn is not a list" % MYNAME())
			return None

		# Create the column item
		for column in listColumn:
			self.text += "| %s " % column
		self.text += "|" + ENDLINE

		# Create the table marking for markdown
		for idx, column in enumerate(listColumn):
			if idx == 0:
				self.text += "| --- "
			elif idx == len(listColumn) - 1:
				self.text += "| ---:"
			else:
				self.text += "| :---: "
		self.text += "|" + ENDLINE

		self.init = True
		return True

	def AddRow(self, listColumn):
		if not type(listColumn) is list:
			print("%s(), listColumn is not a list, it's %s" % (MYNAME(), str(type(listColumn))))
			return None
		if self.init != True:
			print("%s(), table is not created yet" % MYNAME())
			return None

		for column in listColumn:
			self.text += "| %s " % column
		self.text += "|" + ENDLINE
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
			"Method": "",			# 0
			"BlockSize": "",		# 1
			"KeySize": "",			# 2
			"TimeRunning": "",		# 3
			"ActualTime": "",		# 4
			"ResultTimes": "",		# 5
			"Ops": "",				# 6
		}

	@staticmethod
	def MarkdownTableLayoutModel():
		return [
			"Method",
			"Block Size",
			"Time Running",
			"Actual Time Soft",
			"Actual Time Hard",
			"Result Times Soft",
			"Result Times Hard",
			"Throughput Soft",
			"Throughput Hard"]

	@staticmethod
	def GetOpsNonPublicContent(content):
		upperFilter = "The 'numbers' are in 1000s of bytes per second processed."
		belowFilter = "sign    verify    sign/s verify/s"
		if upperFilter in content:
			upperIdx = content.index(upperFilter)
		else:
			return ""
		if belowFilter in content:
			belowIdx = content.index(belowFilter)
		else:
			return ""
		return content[upperIdx:belowIdx]

	@staticmethod
	def ParseNonPublicResult(content, debugLevel=0):
		# Some non-public key cryptography parser
		#                           #0       #1      #2                 #3   #4          #5
		match = re.findall(r'Doing (.+) for (.+) on (.+) size blocks: (\d+) (.+)\'s in ([\d.]+)s', content)

		contentOps = ResultParser.GetOpsNonPublicContent(content)
		# Ops for non-public key parser
		#                            #0             #1               #2                #3           #4               #5
		#                            method         16B              64B               256B         1024B            8192B
		# matchOps = re.findall(r'^([\w\d()\.]+)\s+', content)
		matchOps = re.findall(
			r'^([\w\d()-\.]+)\s+([\w\d()\.]+)\s+([\w\d()\.]+)\s+([\w\d()\.]+)\s+([\w\d()\.]+)\s+([\w\d()\.]+)',
			contentOps,
			re.MULTILINE
		)
		if debugLevel >= 2:
			print (contentOps)
			print (matchOps)
		resultList = []
		for item in match:
			convertedDict = ResultParser.DictModel()
			method = item[0]
			timeRunning = item[1]
			blockSize = item[2]
			resultTimes = item[3]
			method_2nd = item[4]
			actualTime = item[5]
			ops = ""
			for i1 in matchOps:
				if i1[0] != method:
					continue
				if "16" == blockSize:
					ops = i1[1]
				if "64" == blockSize:
					ops = i1[2]
				if "256" == blockSize:
					ops = i1[3]
				if "1024" == blockSize:
					ops = i1[4]
				if "8192" == blockSize:
					ops = i1[5]
			if method != method_2nd:
				print ("method != method_2nd, something error !!!")
				continue
			# print(method, blockSize, timeRunning, resultTimes, actualTime)
			convertedDict["Method"] = method
			convertedDict["BlockSize"] = blockSize
			convertedDict["TimeRunning"] = timeRunning
			convertedDict["ActualTime"] = actualTime
			convertedDict["ResultTimes"] = resultTimes
			convertedDict["Ops"] = ops
			resultList.append(convertedDict)
		return resultList

	@staticmethod
	def GetOpsPublicContent(content):
		"""
		Because each public crypto has its own section in "sign    verify    sign/s verify/s" `seperator`
		This function will return a list of these section
		"""
		seperator = "sign    verify    sign/s verify/s"
		idx = 0
		listIdx = []
		result = []
		while True:
			if content.find(seperator, idx) != -1:
				idx = content.find(seperator, idx)
				listIdx.append(idx)
				idx += 1
			else:
				break
		for i, idx in enumerate(listIdx):
			if i != len(listIdx) - 1:
				result.append(content[idx:listIdx[i+1]])
			else:
				result.append(content[idx:])
		return result

	@staticmethod
	def ParsePublicResult(content, debugLevel=0):
		# Parse the public key cryptography result
		#                           #0        #1           #2      #3   #4       #5         $6
		match = re.findall(r'Doing (\d+) bit (.+)\'s for (\d+)s: (\d+) (\d+) bit (.+) in ([\d\.]+)s', content)

		matchOpsFinal = []
		contentOps = ResultParser.GetOpsPublicContent(content)
		if debugLevel >= 3:
			print ("contentOps list:")
			print (">"*70)
			for item in contentOps:
				print (item)
			print ("<"*70)
		for contentOpsValue in contentOps:
			# This parser for rsa, dsa
			matchOps = re.findall(
				#   #0    #1          #2         #3           #4           #5
				#  method  keysize    sign      verify       sign_ops     verify_ops
				r'^(\w+)\s+(\d+) bits ([\d\.]+)s ([\d\.]+)s\s+([\d\.]+)\s+([\d\.]+)$',
				contentOpsValue,
				re.MULTILINE
			)
			if matchOps != []:
				for i1 in matchOps:
					if debugLevel >= 2:
						print (i1)
					# method, block, sign_ops, verify_ops
					l1 = [i1[0], i1[1], i1[4], i1[5]]
					matchOpsFinal.append(l1)

			# This parser for ecdsa
			matchOps = re.findall(
				#     #0          #1              #2            #3          #4           #5
				#     keysize     method          sign          verify      sign_ops     verify_ops
				r'^\s+(\d+) bit ([\w]+)[()\d\w\s]+\s+([\d\.]+)s\s+([\d\.]+)s\s+([\d\.]+)\s+([\d\.]+)$',
				contentOpsValue,
				re.MULTILINE
			)
			if matchOps != []:
				for i1 in matchOps:
					if debugLevel >= 2:
						print (i1)
					# method, block, sign_ops, verify_ops
					l1 = [i1[1], i1[0], i1[4], i1[5]]
					matchOpsFinal.append(l1)
		if debugLevel >= 3:
			print ("matchOpsFinal list:")
			for item in matchOpsFinal:
				print (item)

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
			ops = ""
			for i1 in matchOpsFinal:
				if keySize != i1[1]:
					continue
				if i1[0] not in method:
					continue
				if "sign" in method:
					ops = i1[2]
				if "verify" in method:
					ops = i1[3]

			if keySize != keySize_2nd:
				print("keySize != keySize_2nd, something error !!!")
				continue
			# print(method, keySize, timeRunning, resultTimes, actualTime)
			convertedDict["Method"] = method
			convertedDict["KeySize"] = keySize
			convertedDict["TimeRunning"] = timeRunning
			convertedDict["ActualTime"] = actualTime
			convertedDict["ResultTimes"] = resultTimes
			convertedDict["Ops"] = ops
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

	parser.add_option(  "--fsoft",
						dest="filePathSoft",
						type="string",
						default="",
						help="point to path of software result file to parse")
	parser.add_option(  "--fhard",
						dest="filePathHard",
						type="string",
						default="",
						help="point to path of hardware result file to parse")
	parser.add_option(  "-o", "--out",
						dest="outFile",
						type="string",
						default="",
						help="result markdown file to dump to")
	parser.add_option(  "-d", "--dump",
						dest="dump",
						action="store_true",
						default=False,
						help="Dump result to stdout")
	(options, args) = parser.parse_args()

	#########################################################
	# Process the input param
	# Strip of file:// if any
	fileProtocolPrefix = "file:///"
	fileSoft = options.filePathSoft
	if fileSoft.startswith(fileProtocolPrefix):
		fileSoft = fileSoft[len(fileProtocolPrefix)-1:]
	fileHard = options.filePathHard
	if fileHard.startswith(fileProtocolPrefix):
		fileHard = fileHard[len(fileProtocolPrefix)-1:]

	# Check file is invalid
	if fileSoft == "":
		print("Please specify software result file path with flag -fsoft")
		sys.exit(1)
	if fileHard == "":
		print("Please specify hardware result file path with flag -fhard")
		sys.exit(1)

	if not os.path.isfile(fileSoft):
		print("File path %s not found" % (fileSoft))
		sys.exit(1)
	if not os.path.isfile(fileHard):
		print("File path %s not found" % (fileHard))
		sys.exit(1)

	#########################################################
	# Open and read the file
	f = open(fileSoft, 'rU')
	fileContentSoft = f.read()
	f.close()
	f = open(fileHard, 'rU')
	fileContentHard = f.read()
	f.close()

	#########################################################
	# Now create the result
	nonPublicResultSoft = ResultParser.ParseNonPublicResult(fileContentSoft)
	publicResultSoft = ResultParser.ParsePublicResult(fileContentSoft)
	ecdhResultSoft = ResultParser.ParseECDHResult(fileContentSoft)

	nonPublicResultHard = ResultParser.ParseNonPublicResult(fileContentHard)
	publicResultHard = ResultParser.ParsePublicResult(fileContentHard)
	ecdhResultHard = ResultParser.ParseECDHResult(fileContentHard)

	#########################################################
	# Now generate the tables
	# Firstly, generate the nonPublicTable
	nonPublicTableLayout = ResultParser.MarkdownTableLayoutModel()
	nonPublicTable = MardownTableGenerator()
	nonPublicTable.CreateTable(nonPublicTableLayout)
	for idx, item in enumerate(nonPublicResultSoft):
		nonPublicTableRow = [
			item["Method"],
			item["BlockSize"],
			item["TimeRunning"],
			item["ActualTime"],
			nonPublicResultHard[idx]["ActualTime"],
			item["ResultTimes"],
			nonPublicResultHard[idx]["ResultTimes"],
			item["Ops"],
			nonPublicResultHard[idx]["Ops"],
		]
		nonPublicTable.AddRow(nonPublicTableRow)

	# Secondly, generate the publicTable
	publicTableLayout = ResultParser.MarkdownTableLayoutModel()
	publicTable = MardownTableGenerator()
	publicTable.CreateTable(publicTableLayout)
	for idx, item in enumerate(publicResultSoft):
		publicTableRow = [
			item["Method"],
			item["KeySize"],
			item["TimeRunning"],
			item["ActualTime"],
			publicResultHard[idx]["ActualTime"],
			item["ResultTimes"],
			publicResultHard[idx]["ResultTimes"],
			item["Ops"],
			publicResultHard[idx]["Ops"],
		]
		publicTable.AddRow(publicTableRow)

	# Thirdly, generate the ecdhTable
	ecdhTableLayout = ResultParser.MarkdownTableLayoutModel()
	ecdhTable = MardownTableGenerator()
	ecdhTable.CreateTable(ecdhTableLayout)
	for idx, item in enumerate(ecdhResultSoft):
		ecdhTableRow = [
			item["Method"],
			item["KeySize"],
			item["TimeRunning"],
			item["ActualTime"],
			ecdhResultHard[idx]["ActualTime"],
			item["ResultTimes"],
			ecdhResultHard[idx]["ResultTimes"]]
		ecdhTable.AddRow(ecdhTableRow)

	if options.dump == True:
		print(nonPublicTable.Table())
		print(publicTable.Table())
		print(ecdhTable.Table())

	if options.outFile != "":
		contentFile = "# Non Public Key Cryptography" + ENDLINE + ENDLINE
		contentFile += nonPublicTable.Table() + ENDLINE
		contentFile += "# Public Key Cryptography" + ENDLINE + ENDLINE
		contentFile += publicTable.Table() + ENDLINE
		contentFile += "# ECDH Cryptography" + ENDLINE + ENDLINE
		contentFile += ecdhTable.Table()

		if not(options.outFile.endswith('.md')):
			nameGenScript = options.outFile + '.md'
		else:
			nameGenScript = options.outFile
		with open(nameGenScript, "w") as f:
			f.write(contentFile)
			f.close()

if __name__ == "__main__":
	main()
