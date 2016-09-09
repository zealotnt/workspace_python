from subprocess import call, check_output
import json
import re
import base64
import md5

def getContentOfrodata(string):
	textToFind = "Contents of section .rodata:"
	idx = string.find(textToFind)
	if idx != -1:
		return string[idx + len(textToFind):].strip('\r\n')
	else:
		print "Can't find rodata pattern"
		return ""

def getLineContent(string):
	return string[43:]

def getRodata(path):
	output = ""
	metadata_out = check_output(["objdump", "-s", "-j", ".rodata", path])
	rodata = getContentOfrodata(metadata_out)
	for line in rodata.splitlines():
		output += getLineContent(line)
	return output

def packJson(name, metadata, binary):
	fileBase64 = base64.standard_b64encode(binary)
	fileMd5 = md5.new()
	fileMd5.update(binary)
	return json.dumps({ str(name + "_metadata"): metadata,
						str(name + "_md5"): fileMd5.hexdigest(),
						str(name + "_fw"): fileBase64 })

def writeJsonFile(path, jsondata):
	fh = open(path, 'wb')
	fh.write(jsondata)
	fh.close()