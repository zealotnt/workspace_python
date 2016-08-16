#!/usr/bin/python

import json
import sys
import mlsFwPack
import os

merged_dict = dict()
output_name = ""

for idx, file in enumerate(sys.argv):
	if idx == 0:
		continue
	if idx == len(sys.argv) - 1:
		output_name = file
		print "--> Output file should be" + output_name
		continue
	print "Found: " + str(file)
	json_text = open(file, 'rb').read()
	json_decoded = json.loads(json_text)
	new_combine = {key: value for (key, value) in (json_decoded.items() + merged_dict.items())}
	merged_dict = new_combine
	idx += 1

output = json.dumps(merged_dict)

json_out_name = "output/" + output_name + ".json"
tar_out_name = "output/" + output_name + ".json.tar.xz"

mlsFwPack.writeJsonFile(json_out_name, output)
tarCmd = "tar --xz -cvf " + tar_out_name + " " + json_out_name
os.system(tarCmd)

# example usage:
# python mergeJsons.py /home/zealot/eclipseMars/workspace_Bluefin/BBB-AppDevelopment/testSerialBBB/Release-Board-Service/svc.json /home/zealot/eclipseMars/workspace_Bluefin/BBB-AppDevelopment/testSerialBBB/Release-Board-Slave/xmsdk.json /home/zealot/workspace_test/surisdk_local/Debug_deploy/surisdk_local.json /home/zealot/miscTest/siriustestbuild_4/suribootloader/Debug_deploy/suribootloader.json allTogether
#-> All fw

# python mergeJsons.py /home/zealot/eclipseMars/workspace_Bluefin/BBB-AppDevelopment/testSerialBBB/Release-Board-Slave/xmsdk.json /home/zealot/workspace_test/surisdk_local/Debug_deploy/surisdk_local.json merge2