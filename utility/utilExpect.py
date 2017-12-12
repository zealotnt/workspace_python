#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-12-11 17:50:10

# ---- IMPORTS
import re
import time
import struct
import sys
import git
import os
import inspect
from optparse import OptionParser, OptionGroup
def get_git_root():
	CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep
	path = CURRENT_DIR
	git_repo = git.Repo(path, search_parent_directories=True)
	git_root = git_repo.git.rev_parse("--show-toplevel")
	return git_root
sys.path.insert(0, get_git_root() + '/test_expect')
from pyexpect_common import *
from template_ifconfig_ip import *
from template_scp import *
from template_ssh import *
sys.path.insert(0, get_git_root() + '/test_bluefinserial/bluefinserial')
from utils import *

class ExpectActions():
	ACTION_CONNECT = "c"
	ACTION_UPLOAD = "u"
	ACTION_DOWNLOAD = "d"
	SUPPORT_ACTION = [ACTION_CONNECT, ACTION_DOWNLOAD, ACTION_UPLOAD]

	def __init__(self, config=""):
		"""
		"""
		if config != "":
			if not os.path.isfile(config):
				print_err("%s does not exist, use default env file" % config)
			else:
				load_dotenv(config, verbose=True)
		self.func = None
		self.target_ip = os.environ.get('TARGET_IP')
		self.target_name = os.environ.get('TARGET_USERNAME')
		self.target_pass = os.environ.get('TARGET_PASSWORD')

	@staticmethod
	def SupportedActionsStr():
		return "/".join(list(ExpectActions.SUPPORT_ACTION))

	def SetValue(self, target_ip, target_name, target_pass):
		self.target_ip = os.environ.get('TARGET_IP') if target_ip == "" else target_ip
		self.target_name = os.environ.get('TARGET_USERNAME') if target_name == "" else target_name
		self.target_pass = os.environ.get('TARGET_PASSWORD') if target_pass == "" else target_pass

	def Connect(self, *kargs):
		SshLoginInteractive(self.target_ip, self.target_name, self.target_pass)

	def Download(self, *kargs):
		# target_item, local_path, to_local_item=""
		ScpDownloadFrom(target_item,
						self.target_name,
						self.target_pass,
						self.target_ip,
						local_path+to_local_item,
						os.environ.get('HOST_USERNAME'))

	def Upload(self, *kargs):
		# target_path, local_target, to_target_item=""
		ScpUploadTo(local_target,
					self.target_name,
					self.target_pass,
					self.target_ip,
					target_path+to_target_item,
					os.environ.get('HOST_USERNAME'))

	def ParseAction(self, action):
		actions = {
			self.ACTION_CONNECT: self.Connect,
			self.ACTION_UPLOAD: self.Upload,
			self.ACTION_DOWNLOAD: self.Download,
		}
		# Get the function from actions dictionary, func is None if no key is matched
		self.func = actions.get(action, None)
		return self.func

	def DoAction(self, *kargs):
		return self.func(kargs)

def main():
	parser = OptionParser()
	parser.add_option(  "-e", "--env-file",
						dest="env_file",
						type="string",
						default="",
						help="the environment file to use, if not specified, the default one in test_expect folder will be used")
	parser.add_option(  "-a", "--action",
						dest="do_action",
						type="string",
						default="",
						help="action for this script to do, supported: %s" % ExpectActions.SupportedActionsStr())
	parser.add_option(  "-c", "--config",
						dest="do_config",
						action="store_true",
						default=False,
						help="do config network interface on local machine, use the info in default env file")
	parser.add_option(  "--target-ip",
						dest="remote_host_ip",
						type="string",
						default="",
						help="IP address of remote machine to interact with")
	parser.add_option(  "--target-name",
						dest="remote_host_name",
						type="string",
						default="",
						help="User name of remote machine to interact with")
	parser.add_option(  "--target-pass",
						dest="remote_host_pass",
						type="string",
						default="",
						help="User's password of remote machine to interact with")
	parser.add_option(  "--host-iface",
						dest="host_iface",
						type="string",
						default="",
						help="Host's interface")
	(options, args) = parser.parse_args()

	if options.do_action == "":
		parser.print_help()
		print_err("DO_ACTION is required")
		sys.exit(-1)
	if options.do_config:
		SetNetworkInterface(HOST_INTERFACE, HOST_IP, HOST_PASSWORD)

	pyExpectedActions = ExpectActions(options.env_file)
	pyExpectedActions.SetValue(options.remote_host_ip, options.remote_host_name, options.remote_host_pass)
	action = pyExpectedActions.ParseAction(options.do_action)
	if action == None:
		print_err("Action \"%s\" not supported" % (options.do_action))
		sys.exit(-1)
	pyExpectedActions.DoAction()

if __name__ == "__main__":
	main()
