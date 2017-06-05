#!/usr/bin/python
# cd ${ProjDirPath}/${ConfigName}
# python ../scripts/xmsdkPack.py ${ConfigName} ${BuildArtifactFileName}

import mlsFwPack
import sys
import os

def usage():
	print "Usage: " + sys.argv[0] + " <buildDirectory>"

if len(sys.argv) != 3:
	print "Syntax error"
	usage()
	exit(1)

buildDir = sys.argv[1]
buildObj = sys.argv[2]

pathToObject 	= "../" + buildDir + "/src/mlsApp/src/version.o"
pathToBin 		= "../" + buildDir + "/" + buildObj
pathOutput 		= "../" + buildDir + "/" + buildObj + ".json"

xmsdkMetadata = mlsFwPack.getRodata(pathToObject)

xmsdkBinary = open(pathToBin, 'rb').read()

xmsdkJson = mlsFwPack.packJson(buildObj, xmsdkMetadata, xmsdkBinary)

mlsFwPack.writeJsonFile(pathOutput, xmsdkJson)

print "Write successfully to " + pathOutput

jsonFileName = "../" + buildDir + "/" + buildObj + ".json"
tarFileName = "../" + buildDir + "/" + buildObj + ".json.tar.xz"
tarCmd = "tar --xz -cvf " + tarFileName + " " + jsonFileName
os.system(tarCmd)
