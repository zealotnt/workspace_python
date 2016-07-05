#!/usr/bin/python

import mlsFwPack

surisdkMetadata = mlsFwPack.getRodata("output/suri_version.o")

surisdkBinary = open("output/surisdk_local.tar.gz", 'rb').read()
# surisdkBinary = open("output/surisdk_wrong_packed.tar.gz", 'rb').read()

surisdkJson = mlsFwPack.packJson("surisdk", surisdkMetadata, surisdkBinary)

mlsFwPack.writeJsonFile("output/surisdk.json", surisdkJson)
