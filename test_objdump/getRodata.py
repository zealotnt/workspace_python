#!/usr/bin/python

from subprocess import call, check_output
import json
import re
import termcolor
import base64

output = ""

def BeginSection(string):
	print termcolor.colored("\r\n\t" + string, 'green')

def getContentOfrodata(string):
	textToFind = "Contents of section .rodata:"
	idx = string.find(textToFind)
	return string[idx + len(textToFind):].strip('\r\n')

def getLineContent(string):
	return string[43:]

def getRodata(path):
	output = ""
	metadata_out = check_output(["objdump", "-s", "-j", ".rodata", path])
	rodata = getContentOfrodata(metadata_out)
	for line in rodata.splitlines():
		output += getLineContent(line)
	return output


BeginSection("objdump output:")
xm_metadata_out = check_output(["objdump", "-s", "-j", ".rodata", "/home/zealot/workspace_test/xmsdk_local/Debug-Board-Slave/src/mlsApp/src/version.o"])
print xm_metadata_out

BeginSection("Get rodata:")
rodata = getContentOfrodata(xm_metadata_out)
print rodata

BeginSection("Extraction:")
for line in rodata.splitlines():
	output += getLineContent(line)
print output

BeginSection("All in one:")
xm_metadata_out = getRodata("/home/zealot/workspace_test/xmsdk_local/Debug-Board-Slave/src/mlsApp/src/version.o")

xmsdkBinary = open("/home/zealot/workspace_test/xmsdk_local/Debug-Board-Slave/xmsdk", 'rb').read()
print "Size of xmsdk: " + str(len(xmsdkBinary)) + " (bytes)"
xmsdkBase64 = base64.b64encode(xmsdkBinary)
print "Size of xmsdkBase64: " + str(len(xmsdkBase64)) + " (bytes)"
print "xmsdkBase64 is bigger " + str(float(float(len(xmsdkBase64))/float(len(xmsdkBinary)))) + " times"

xmsdk_json = json.dumps([ { "xmsdk_metadata": xm_metadata_out, "xmsdk_fw": xmsdkBase64 } ])
fh = open("xmsdk.json", 'wb')
fh.write(xmsdk_json)
fh.close()