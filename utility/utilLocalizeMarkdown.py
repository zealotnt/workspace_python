#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2018-01-31 00:21:20
#
# utilLocalizeMarkdown.py


# ---- IMPORTS
import os
import sys
import re
import shutil
import imghdr
import textwrap
from optparse import OptionParser, OptionGroup
import colorama
import urllib, urlparse
import git, inspect
def get_git_root():
	CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep
	path = CURRENT_DIR
	git_repo = git.Repo(path, search_parent_directories=True)
	git_root = git_repo.git.rev_parse("--show-toplevel")
	return git_root
sys.path.insert(0, get_git_root() + '/test_bluefinserial/bluefinserial')
from utils import *
# https://stackoverflow.com/questions/27981545/suppress-insecurerequestwarning-unverified-https-request-is-being-made-in-pytho
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---- CONSTANTS

# ---- GLOBALS
def download_file(url, download_file_name):
	# https://stackoverflow.com/questions/33488179/how-do-i-download-pdf-file-over-https-with-python
	# Better comparison: https://stackoverflow.com/a/45279314
	import requests
	r = requests.get(url, verify=False, stream=True)
	r.raw.decode_content = True
	with open(download_file_name, 'wb') as f:
		shutil.copyfileobj(r.raw, f)

def print_err(text):
	print (colorama.Fore.RED + "Error: " + text + colorama.Style.RESET_ALL)

def print_noti(text):
	print (colorama.Fore.YELLOW + text + colorama.Style.RESET_ALL)

def is_external_link(link):
	return True

def rchop(thestring, ending):
	# https://stackoverflow.com/questions/3663450/python-remove-substring-only-at-the-end-of-string
	if thestring.endswith(ending):
		return thestring[:-len(ending)]
	return thestring

def start_meld(original_file, new_file):
	os.system("meld %s %s" % (original_file, new_file))

def main():
	EPILOG = textwrap.dedent(
	"""
	This script will search all images in markdown file and download to local in pics folder,
	and change the content in markdown file to use the local images.
	""")
	parser = OptionParser(epilog=EPILOG)
	parser.add_option(  "-f",
						dest="file_path",
						type="string",
						help="path to markdown file to be localized")
	(options, args) = parser.parse_args()

	if options.file_path is None:
		parser.print_help()
		print_err("markdown file path is required")
		sys.exit(-1)

	colorama.init()
	markdown_file_path = options.file_path
	markdown_file_name_full = os.path.basename(markdown_file_path)
	markdown_file_name = os.path.splitext(markdown_file_name_full)[0]
	if not os.path.isfile(markdown_file_path):
		print_err("%s does not exist" % markdown_file_path)
		sys.exit(-1)

	with open(markdown_file_path, "r") as f:
		content = []
		for line in f:
			content.append(line)

		pics_count = 0
		# Create the pics folder if not created
		if not os.path.exists("pics"):
			os.makedirs("pics")

		# Loop through line by line
		for idx, line in enumerate(content):
			# Find line that contain the image link
			image_line_patters = [
				r'!\[(.*)\]\(([\S]+)\s*".+"\)',
				r"!\[(.*)\]\((.+)\)",
			]
			for pattern in image_line_patters:
				match = re.findall(pattern, line, re.MULTILINE)
				# There should not more than 2 image in one line
				if len(match) == 1:
					image_url = match[0][1]
					image_url_org = image_url
					# check if the image is from the internet
					if is_external_link(image_url) == False:
						print_noti("Image %s is not from internet, ignore" % image_url)
						continue

					print_noti("We get image: %s" % image_url)

					# download the image
					# https://stackoverflow.com/questions/3663450/python-remove-substring-only-at-the-end-of-string
					image_url = rchop(image_url, "/")
					# https://stackoverflow.com/questions/18727347/how-to-extract-a-filename-from-a-url-append-a-word-to-it
					to_download = os.path.basename(urlparse.urlparse(image_url).path)
					download_file(image_url, to_download)
					# TODO: should check ok

					# extract extension from file-name seems not works, because some file has weird ending text
					# extension = os.path.splitext(to_download)[1]
					# => so we calculate image type by using python's imghdr
					# https://docs.python.org/2/library/imghdr.html
					extension = imghdr.what(to_download)

					# put the downloaded image with file name pattern: pics/<md-file-name>-<pic-count>
					new_location = "./pics/%s-%d.%s" % (markdown_file_name, pics_count, extension)
					print_noti("\t=> Save to %s" % new_location)
					shutil.move(to_download, new_location)
					pics_count += 1

					# we should use image_url_org, cause sometimes, a link has a trailling / in it
					# -> markdown file protocol can't render the image
					content[idx] = content[idx].replace(image_url_org, new_location)
					# if match one pattern, don't check other pattern
					# the last pattern is the most adpopt type, could be errorneous in some case
					break

		# Create new markdown file, with file name: <md-file-name>.new.md
		markdown_new_file = markdown_file_name + ".new.md"
		new_md_file = open(markdown_new_file, 'w')
		for item in content:
			new_md_file.write("%s" % item)
		new_md_file.close()

		if yes_or_no("Do you want to compare: %s (org) and %s (new) ?" %
			(make_green(markdown_file_name_full), make_yellow(markdown_new_file))) == True:
			start_meld(markdown_file_path, markdown_new_file)

			if yes_or_no("Is it seem ok, replace %s with %s ?" %
				(make_green(markdown_file_name_full), make_yellow(markdown_new_file))) == True:
				shutil.move(markdown_new_file, markdown_file_path)

# ---- MAIN
if __name__ == "__main__":
	main()
