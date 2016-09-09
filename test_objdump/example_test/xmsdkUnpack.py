#!/usr/bin/python

from subprocess import call, check_output
import json
import re
import termcolor
import base64



fh = open("xmsdk.json", 'r')
decoded = json.loads(fh.read())
xmsdkBinary = base64.b64decode(decoded["xmsdk_fw"])

fh = open("xmsdk", 'wb')
fh.write(xmsdkBinary)
fh.close()

print decoded["xmsdk_metadata"]