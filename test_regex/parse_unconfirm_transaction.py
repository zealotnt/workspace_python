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

class ResultParser():
	@staticmethod
	def DictModel():
		return {
			"ALL": "",
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
	inputDat["DETECT"] = inputDat["TOTAL_DETECT"] / times
	inputDat["READ"] = inputDat["TOTAL_READ"] / times
	inputDat["WRITE"] = inputDat["TOTAL_WRITE"] / times
	return inputDat

def ParseTime(content):
	timeData = []
	match = re.findall(r'Detect: (\d+) ms, Read: (\d+) ms, Write: (\d+) ms', content)
	for idx, item in enumerate(match):
		timeData.append(int(item[0]))
		timeData.append(int(item[1]))
		timeData.append(int(item[2]))
	return timeData

def ParseNocard(content, debugLevel=0):
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
		convertedDict["IDX_END"] = endIdx
		resultList.append(convertedDict)

		if debugLevel > 2:
			print ">"*80
			print "SECTION=%d" % idx
			for idx, item in enumerate(convertedDict["DETECTING_CARD"]):
				print idx
				print item
			print "<"*80
			print ""
			print ""
			print ""

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
			"IDX": 100,
			"VAL": 100,
		},
		"READ": {
			"IDX": 100,
			"VAL": 100,
		},
		"WRITE": {
			"IDX": 100,
			"VAL": 100,
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
	}
	unconfirmData = {
		"TIMES": 0,
		"AT": []
	}

	for idx, item in enumerate(resultList):
		if 1:
			# Result for unconfirm
			if len(item["DETECTING_CARD"]) > 1:
				dataAtFirstDetection = item["DETECTING_CARD"][1]
				if IsUnconfirm(dataAtFirstDetection):
					if debugLevel > 1:
						print("Unconfirm at SECTION=%d" % idx)
					unconfirmData["TIMES"] += 1
					unconfirmData["AT"].append(idx)

			# Result for success
			if len(item["DETECTING_CARD"]) >= 3:
				if debugLevel > 1:
					print("Success at SECTION=%d" % idx)

				dataAtFirstSuccess = item["DETECTING_CARD"][1]
				timingData = ParseTime(dataAtFirstSuccess)
				if len(timingData) != 3:
					continue
				if debugLevel > 1:
					print (timingData)

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

	avgNumbers = CalAverate(avgNumbers)

	print ("")
	print ("")
	print ("RESULT")
	print ("SUCCESS %d times" % avgNumbers["TIMES"])
	print ("DETECT: MAX = %d, MIN = %d, AVG = %d" % (
		maxNumbers["DETECT"]["VAL"],
		minNumbers["DETECT"]["VAL"],
		avgNumbers["DETECT"])
	)
	print ("READ: MAX = %d, MIN = %d, AVG = %d" % (
		maxNumbers["READ"]["VAL"],
		minNumbers["READ"]["VAL"],
		avgNumbers["READ"])
	)
	print ("WRITE: MAX = %d, MIN = %d, AVG = %d" % (
		maxNumbers["WRITE"]["VAL"],
		minNumbers["WRITE"]["VAL"],
		avgNumbers["WRITE"])
	)
	print ("UNCONFIRM %d times, at " % (unconfirmData["TIMES"]), unconfirmData["AT"])
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
	f = open(options.file, 'rb')
	fileContent = f.read()
	f.close()

	#########################################################
	# Break the result into chunk of Nocard detected
	# we should have a list
	# print fileContent
	noCardList = ParseNocard(fileContent, debugLevel=int(options.debugLevel))
	# ParseUnconfirm(noCardList)

	#########################################################
	# The next one of Nocard detection, if it detect CEPAS, and has a code C0
	# then it is an unconfirm transaction

if __name__ == "__main__":
	main()
