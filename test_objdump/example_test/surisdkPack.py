#!/usr/bin/python
# cd ${ProjDirPath}/${ConfigName}
# python ../script/surisdkPack.py
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

pathToObject 	= "../" + buildDir + "/source/styl/mlsApp/src/version.o"
pathToBin 		= "../" + buildDir + "/" + buildObj + ".bin"
pathOutput 		= "../" + buildDir + "/" + buildObj + ".json"

surisdkMetadata = mlsFwPack.getRodata(pathToObject)

surisdkBinary = open(pathToBin, 'rb').read()

surisdkJson = mlsFwPack.packJson("surisdk", surisdkMetadata, surisdkBinary)

mlsFwPack.writeJsonFile(pathOutput, surisdkJson)

print "Write successfully to " + pathOutput

jsonFileName = "../" + buildDir + "/" + buildObj + ".json"
tarFileName = "../" + buildDir + "/" + buildObj + ".json.tar.xz"
tarCmd = "tar --xz -cvf " + tarFileName + " " + jsonFileName
os.system(tarCmd)
