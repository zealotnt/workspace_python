#!/bin/bash
python mergeJsons.py /home/zealot/eclipseMars/workspace_Bluefin/BBB-AppDevelopment/testSerialBBB/Release-Board-Service/svc.json /home/zealot/eclipseMars/workspace_Bluefin/BBB-AppDevelopment/testSerialBBB/Release-Board-Slave/xmsdk.json /home/zealot/workspace_test/surisdk_local/Debug_deploy/surisdk_local.json /home/zealot/miscTest/siriustestbuild_4/suribootloader/Debug_deploy/suribootloader.json allTogether

python mergeJsons.py /home/zealot/eclipseMars/workspace_Bluefin/BBB-AppDevelopment/testSerialBBB/Release-Board-Slave/xmsdk.json /home/zealot/workspace_test/surisdk_local/Debug_deploy/surisdk_local.json merge2
