#!/usr/bin/python

import json
import mlsFwPack
import os

################### Build surisdk.json ###############################
surisdkMetadata = mlsFwPack.getRodata("output/suri_version.o")

# surisdkBinary = open("output/surisdk_local.tar.gz", 'rb').read()
# surisdkBinary = open("output/surisdk_020000.tar.gz", 'rb').read()
surisdkBinary = open("output/surisdk_020000_Os.tar.gz", 'rb').read()
# surisdkBinary = open("output/surisdk_wrong_packed.tar.gz", 'rb').read()

surisdkJson = mlsFwPack.packJson("surisdk", surisdkMetadata, surisdkBinary)
mlsFwPack.writeJsonFile("output/surisdk.json", surisdkJson)


################### Build xmsdk.json ###############################
xmsdkMetadata = mlsFwPack.getRodata("output/xm_version.o")
xmsdkBinary = open("/home/zealot/eclipseMars/workspace_Bluefin/BBB-AppDevelopment/testSerialBBB/Debug-Board-Slave/xmsdk", 'rb').read()
xmsdkJson = mlsFwPack.packJson("xmsdk", xmsdkMetadata, xmsdkBinary)
mlsFwPack.writeJsonFile("output/xmsdk.json", xmsdkJson)


################### Build merge.json ###############################
xmsdkJson = open("output/xmsdk.json", 'rb').read()
xmsdk = json.loads(xmsdkJson)
print xmsdk["xmsdk_metadata"]
print xmsdk["xmsdk_md5"]

surisdkJson = open("output/surisdk.json", 'rb').read()
surisdk = json.loads(surisdkJson)
print surisdk["surisdk_metadata"]
print surisdk["surisdk_md5"]


merged_dict = {key: value for (key, value) in (surisdk.items() + xmsdk.items())}
output = json.dumps(merged_dict)
mlsFwPack.writeJsonFile("output/merge.json", output)


################### Build merge.json.tar.gz ###############################
os.system("cp output/merge.json .")
os.system("tar -cJf merge.json.tar.xz merge.json")
os.system("rm merge.json")