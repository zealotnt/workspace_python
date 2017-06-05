#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-04-21 08:58:24

import os
import re
import time
import sys
import struct
import inspect
from optparse import OptionParser, OptionGroup

class ResultParser():
	@staticmethod
	def DictModel():
		return {
			"ALL": "",
			"LINE_START": 0,
			"LINE_END": 0,
			"IDX_START": 0,
			"IDX_END": 0,
			"IS_SUCCESS": True,
			"IS_UNCONFIRM": False,
			"IS_READ_ERROR": False,
			"DETECTING_CARD": [],
		}

# def ParseUnconfirm(noCardList):
# 	for idx, item in enumerate(noCardList):
# 		# Break the all log into list of "Detecting Card"
# 		match = re.findall(r'Detecting card.+', item["ALL"])
# 		print idx
# 		# print item["ALL"]
# 		print ""

def ParseDetectingCard(content):
	# Break the all log into list of "Detecting Card"
	match = [(m.start(0), m.end(0)) for m in re.finditer(r'Detecting card.+', content)]
	resultList = []
	for idx, item in enumerate(match):
		startIdx = item[0]
		if idx < len(match) - 1:
			endIdx = match[idx+1][0]
		else:
			endIdx = len(content) - 1
		allLog = content[startIdx:endIdx]
		resultList.append(allLog)
	return resultList

def IsUnconfirm(content):
	if "The card did not respond (0xC0)." in content:
		return True

def CalAverate(inputDat):
	times = inputDat["TIMES"]
	if times != 0:
		inputDat["DETECT"] = inputDat["TOTAL_DETECT"] / times
		inputDat["READ"] = inputDat["TOTAL_READ"] / times
		inputDat["WRITE"] = inputDat["TOTAL_WRITE"] / times
	else:
		print("No success, no average")
	return inputDat

def ParseTime(content):
	timeData = []
	match = re.findall(r'Detect: (\d+) ms, Read: (\d+) ms, Write: (\d+) ms', content)
	for idx, item in enumerate(match):
		timeData.append(int(item[0]))
		timeData.append(int(item[1]))
		timeData.append(int(item[2]))
	return timeData

def GetLineNumber(content, fromIdx):
	line = 0
	for idx, char in enumerate(content):
		if char == '\n':
			line += 1

		if idx >= fromIdx:
			return line
	return line

def ParseNocard(fileName, content, debugLevel=0):
	# match = re.finditer(r'Detecting card.+\[No Card\]', content)
	match = [(m.start(0), m.end(0)) for m in re.finditer(r'Detecting card.+\[No Card\]', content)]
	resultList = []
	# print match
	for idx, item in enumerate(match):
		convertedDict = ResultParser.DictModel()
		startIdx = item[0]
		if idx < len(match) - 1:
			endIdx = match[idx+1][0]
		else:
			endIdx = len(content) - 1
		allLog = content[startIdx:endIdx]

		convertedDict["DETECTING_CARD"] = ParseDetectingCard(allLog)
		convertedDict["ALL"] = allLog
		convertedDict["IDX_START"] = startIdx
		convertedDict["LINE_START"] = GetLineNumber(content, startIdx)
		convertedDict["IDX_END"] = endIdx
		resultList.append(convertedDict)

		if debugLevel >= 2:
			print (">"*80)
			print ("SECTION=%d line=%d" % (idx, convertedDict["LINE_START"]))
			for idx, item in enumerate(convertedDict["DETECTING_CARD"]):
				print (idx)
				print (item)
			print ("<"*80)
			print ("")
			print ("")
			print ("")
	return resultList

def PrintResult(fileName, resultList, debugLevel=0):
	# Print the result
	maxNumbers = {
		"DETECT": {
			"IDX": 0,
			"VAL": 0,
		},
		"READ": {
			"IDX": 0,
			"VAL": 0,
		},
		"WRITE": {
			"IDX": 0,
			"VAL": 0,
		},
	}
	minNumbers = {
		"DETECT": {
			"IDX": 100000,
			"VAL": 100000,
		},
		"READ": {
			"IDX": 100000,
			"VAL": 100000,
		},
		"WRITE": {
			"IDX": 100000,
			"VAL": 100000,
		},
	}
	avgNumbers = {
		"TIMES": 0,
		"TOTAL_DETECT": 0,
		"TOTAL_READ": 0,
		"TOTAL_WRITE": 0,
		"DETECT": 0,
		"READ": 0,
		"WRITE": 0,
		"AT_IDX": [],
		"AT_LINE": []
	}
	unconfirmData = {
		"TIMES": 0,
		"AT_ALL_IDX": [],
		"AT_IDX": [],
		"AT_LINE": []
	}

	for idx, item in enumerate(resultList):
		# Result for unconfirm
		if len(item["DETECTING_CARD"]) > 1:
			dataAtFirstDetection = item["DETECTING_CARD"][1]
			if IsUnconfirm(dataAtFirstDetection):
				if debugLevel >= 1:
					print("Unconfirm at SECTION=%d line=%d" % (idx, item["LINE_START"]))
				unconfirmData["TIMES"] += 1
				unconfirmData["AT_IDX"].append(idx)
				unconfirmData["AT_LINE"].append(item["LINE_START"])
				unconfirmData["AT_ALL_IDX"].append(item["IDX_START"])
				continue

		# Result for success
		if len(item["DETECTING_CARD"]) >= 2:
			dataAtFirstSuccess = item["DETECTING_CARD"][1]
			timingData = ParseTime(dataAtFirstSuccess)
			if len(timingData) != 3:
				if debugLevel >= 1:
					print ("Section %d" % idx)
				continue
			if debugLevel >= 1:
				print("Success at SECTION=%d line=%d Timing data: " % (idx, item["LINE_START"]), timingData)

			if maxNumbers["DETECT"]["VAL"] <= timingData[0]:
				maxNumbers["DETECT"]["VAL"] = timingData[0]
			if minNumbers["DETECT"]["VAL"] >= timingData[0]:
				minNumbers["DETECT"]["VAL"] = timingData[0]

			if maxNumbers["READ"]["VAL"] <= timingData[1]:
				maxNumbers["READ"]["VAL"] = timingData[1]
			if minNumbers["READ"]["VAL"] >= timingData[1]:
				minNumbers["READ"]["VAL"] = timingData[1]

			if maxNumbers["WRITE"]["VAL"] <= timingData[2]:
				maxNumbers["WRITE"]["VAL"] = timingData[2]
			if minNumbers["WRITE"]["VAL"] >= timingData[2]:
				minNumbers["WRITE"]["VAL"] = timingData[2]

			avgNumbers["TIMES"] += 1
			avgNumbers["TOTAL_DETECT"] += timingData[0]
			avgNumbers["TOTAL_READ"] += timingData[1]
			avgNumbers["TOTAL_WRITE"] += timingData[2]

			avgNumbers["AT_LINE"].append(item["LINE_START"])
			avgNumbers["AT_IDX"].append(item["IDX_START"])

	avgNumbers = CalAverate(avgNumbers)

	print ("")
	print ("RESULT of %s" % (fileName))
	print ("")
	print ("SUCCESS %d times at lines" % avgNumbers["TIMES"], avgNumbers["AT_LINE"])
	print ("DETECT: MAX = %4d, MIN = %4d, AVG = %4d" % (
		maxNumbers["DETECT"]["VAL"],
		minNumbers["DETECT"]["VAL"],
		avgNumbers["DETECT"])
	)
	print ("READ:   MAX = %4d, MIN = %4d, AVG = %4d" % (
		maxNumbers["READ"]["VAL"],
		minNumbers["READ"]["VAL"],
		avgNumbers["READ"])
	)
	print ("WRITE:  MAX = %4d, MIN = %4d, AVG = %4d" % (
		maxNumbers["WRITE"]["VAL"],
		minNumbers["WRITE"]["VAL"],
		avgNumbers["WRITE"])
	)

	print ("")
	print ("UNCONFIRM %d times, at lines: " % (unconfirmData["TIMES"]), unconfirmData["AT_LINE"])
	return resultList

def main():
	parser = OptionParser()

	parser.add_option(  "-f",
						dest="file",
						type="string",
						default="",
						help="log file to parse")
	parser.add_option(  "-d",
						dest="debugLevel",
						type="string",
						default="0",
						help="debug level")
	(options, args) = parser.parse_args()

	#########################################################
	# Open and read the file
	f = open(options.file, 'r')
	fileContent = f.read()
	f.close()

	# replace the weird line endings
	fileContent = fileContent.replace('\r\n', '\n')
	fileContent = fileContent.replace('\n\r', '\n')
	fileContent = fileContent.replace('\r', '\n')

	#########################################################
	# Break the result into chunk of Nocard detected
	# we should have a list
	# print fileContent
	noCardList = ParseNocard(options.file, fileContent, debugLevel=int(options.debugLevel))
	PrintResult(options.file, noCardList, debugLevel=int(options.debugLevel))

if __name__ == "__main__":
	main()
