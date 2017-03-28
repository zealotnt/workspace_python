import os
import sys
import time
import subprocess
import re

result = subprocess.check_output("xinput list", shell=True)
print result

touch_id = re.findall(r'SynPS/2 Synaptics TouchPad\s+id=(\d+)', result)
if len(touch_id) != 0:
	print "Touchpad_id = " + touch_id[0]
	os.system("xinput set-prop " + touch_id[0] + " \"Device Enabled\" 0")
else:
	print "Can't find touchpad_id, exit"
	sys.exit(-1)
