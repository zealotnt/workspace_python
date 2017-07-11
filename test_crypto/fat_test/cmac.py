#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-11 14:43:27

import os
import sys
import git
import os
import inspect
def get_git_root():
	CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep
	path = CURRENT_DIR
	git_repo = git.Repo(path, search_parent_directories=True)
	git_root = git_repo.git.rev_parse("--show-toplevel")
	return git_root
sys.path.insert(0, get_git_root() + '/test_bluefinserial/bluefinserial')
from utils import *

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import cmac
from cryptography.hazmat.primitives.ciphers import algorithms

def main():
	message = b"message to authenticate"
	aes_key = os.urandom(32)

	c = cmac.CMAC(algorithms.AES(aes_key), backend=default_backend())
	c.update(message)
	cmacRes = c.finalize()

	# Dump hex value
	dump_hex(
		message,
		'message: ',
		preFormat="C"
	)
	dump_hex(
		aes_key,
		'aes_key: ',
		preFormat="C"
	)
	dump_hex(
		cmacRes,
		'cmac: ',
		preFormat="C"
	)


if __name__ == "__main__":
	main()
