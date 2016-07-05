#!/usr/bin/python

import mlsFwPack

xmsdkMetadata = mlsFwPack.getRodata("output/xm_version.o")
xmsdkBinary = open("output/xmsdk", 'rb').read()

# xmsdkMetadata = mlsFwPack.getRodata("output/xm_version.o")
# xmsdkBinary = open("/home/zealot/eclipseMars/workspace_Bluefin/BBB-AppDevelopment/testSerialBBB/Debug-Board-Slave/xmsdk", 'rb').read()

xmsdkJson = mlsFwPack.packJson("xmsdk", xmsdkMetadata, xmsdkBinary)

mlsFwPack.writeJsonFile("output/xmsdk.json", xmsdkJson)
