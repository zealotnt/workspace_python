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
import yaml
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
	ACTION_UPLOAD_LIST = "ul"
	ACTION_DOWNLOAD_LIST = "dl"
	SUPPORT_ACTION = [ACTION_CONNECT, ACTION_DOWNLOAD, ACTION_DOWNLOAD_LIST, ACTION_UPLOAD, ACTION_UPLOAD_LIST]

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

	def _download(self, download_from, download_to):
		print("=> Downloading %s to %s" % (
			make_yellow(download_from, True),
			make_green(download_to, True)
		))
		ScpDownloadFrom(download_from,
						self.target_name,
						self.target_pass,
						self.target_ip,
						download_to,
						os.environ.get('HOST_USERNAME'))

	def Download(self, *kargs):
		# target_item, local_path, to_local_item=""
		args = kargs[0][0]
		if len(args) != 3 and len(args) != 2:
			print_err("Download requires 2 (1 optional) arguments: <remote-file-to-download> <local-path> [local-name]")
			return None

		target_item = args[0]
		local_path = args[1]
		to_local_item = ""
		if len(args) == 3:
			to_local_item = args[2]
			if not local_path.endswith(os.sep):
				local_path += os.sep
		self._download(target_item, local_path+to_local_item)



	def _upload(self, upload_from, upload_to):
		print("=> Uploading %s to %s" % (
			make_yellow(upload_from, True),
			make_green(upload_to, True)
		))
		ScpUploadTo(upload_from,
					self.target_name,
					self.target_pass,
					self.target_ip,
					upload_to,
					os.environ.get('HOST_USERNAME'))

	def Upload(self, *kargs):
		# target_path, local_target, to_target_item=""
		args = kargs[0][0]
		if len(args) != 3 and len(args) != 2:
			print_err("Upload requires 2 (1 optional) arguments: <local-target-to-upload> <target-path> [target-name]")
			return None

		local_target = args[0]
		target_path = args[1]
		to_target_item = ""
		if len(args) == 3:
			to_target_item = args[2]
			if not target_path.endswith(os.sep):
				target_path += os.sep
		self._upload(local_target, target_path+to_target_item)


	def _validate_yaml_input(self, args, key):
		# conf_file: yaml file that contain instruction to download from host
		if len(args) != 1:
			print_err("Requires 1 argument: <yaml-instruction-file>")
			return None

		conf_file = args[0]
		if not os.path.isfile(conf_file):
			print_err("Yaml config file: %s does not exist, exit" % conf_file)
			return None

		config_parsed = yaml.load(open(conf_file).read())
		# TODO: validate the "config_parsed" dict

		return config_parsed[key]

	def DownloadList(self, *kargs):
		args = kargs[0][0]
		list_files = self._validate_yaml_input(args, "DownloadList")
		if list_files == None:
			return None
		for couple in list_files:
			self._download(couple['from'], couple['to'])

	def UploadList(self, *kargs):
		args = kargs[0][0]
		list_files = self._validate_yaml_input(args, "UploadList")
		if list_files == None:
			return None
		for couple in list_files:
			self._upload(couple['from'], couple['to'])

	def ParseAction(self, action):
		actions = {
			self.ACTION_CONNECT: self.Connect,
			self.ACTION_UPLOAD: self.Upload,
			self.ACTION_DOWNLOAD: self.Download,
			self.ACTION_UPLOAD_LIST: self.UploadList,
			self.ACTION_DOWNLOAD_LIST: self.DownloadList,
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

	group = OptionGroup(parser, make_yellow("Target Options"))
	group.add_option(  "--target-ip",
						dest="remote_host_ip",
						type="string",
						default="",
						help="IP address of remote machine to interact with")
	group.add_option(  "--target-name",
						dest="remote_host_name",
						type="string",
						default="",
						help="User name of remote machine to interact with")
	group.add_option(  "--target-pass",
						dest="remote_host_pass",
						type="string",
						default="",
						help="User's password of remote machine to interact with")
	parser.add_option_group(group)

	group = OptionGroup(parser, make_yellow("Local Host Options"))
	group.add_option(  "--host-iface",
						dest="host_iface",
						type="string",
						default="",
						help="Host's interface")
	parser.add_option_group(group)
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
	pyExpectedActions.DoAction(args)

if __name__ == "__main__":
	main()
