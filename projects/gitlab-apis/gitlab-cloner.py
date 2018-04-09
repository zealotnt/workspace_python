#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2018-04-09 15:27:23
#
# gitlab-cloner.py


# ---- IMPORTS
import gitlab
import pprint
import re
import git, inspect, sys, os
def get_git_root():
	CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep
	path = CURRENT_DIR
	git_repo = git.Repo(path, search_parent_directories=True)
	git_root = git_repo.git.rev_parse("--show-toplevel")
	return git_root
sys.path.insert(0, get_git_root() + '/test_bluefinserial/bluefinserial')
from utils import *
from dotenv import load_dotenv

# ---- CONSTANTS
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path, verbose=True)

# ---- GLOBALS
def get_groups(projects):
	groups = []
	for project in projects:
		# print(project)
		# print(project.http_url_to_repo)
		group = get_group_name(project.http_url_to_repo)
		if group not in groups:
			groups.append(group)
	return groups

def get_group_name(url):
	matches = re.findall(
		r'(http|git)://[^/]+/([^/]+)',
		url,
		re.MULTILINE
	)
	if len(matches) != 1:
		pprint.pprint(matches)
		print("Error with url: %s" % url)
		return None
	return matches[0][1]

def clear_my_gitlab_projects(gl_mine, groups):
	if len(groups) != 0:
		if yes_or_no("Do you want to remove all existing group of gitlab-mine ?") == True:
			groups = gl_mine.groups.list()
			for group in groups:
				print_ok("\tDeleting group id=%d, name=%s" % (group.id, group.name))
				group.delete()
	else:
		print_noti("gitlab-mine has no existing group")

def clone_groups(gl_mine, target_groups):
	print_noti("Cloning group from gitlab-target to gitlab-mine")
	for group_name in target_groups:
		group = gl_mine.groups.create({'name': group_name, 'path': group_name})
		group.save()
		print_ok("\tGroup %s created" % (group_name))

def print_suggest_cloning_url(target_projects):
	gl_account = os.environ.get("GL_TARGET_ACCOUNT")
	gl_pass = os.environ.get("GL_TARGET_PASSWORD")
	print (os.environ.get("GL_TARGET_ACCOUNT"))
	print (os.environ.get("GL_TARGET_PASSWORD"))
	full_urls = []
	for project in target_projects:
		inject_pos = len("http://")
		full_url = (project.http_url_to_repo[:inject_pos] +
					("%s:%s@" % (gl_account, gl_pass)) +
					project.http_url_to_repo[inject_pos:])
		full_urls.append(full_url)
	full_urls.sort()
	print_noti("Suggesting cloning URL:")
	for url in full_urls:
		print("\t%s" % url)

def main():
	gl = gitlab.Gitlab.from_config('gitlab-target', ['gitlab.cfg'])

	target_projects = gl.projects.list(all=True)
	print_suggest_cloning_url(target_projects)

	print_noti("Group from target gitlab server: ")
	target_groups = get_groups(target_projects)
	pprint.pprint(target_groups)

	gl_mine = gitlab.Gitlab.from_config('gitlab-mine', ['gitlab.cfg'])
	my_groups = gl_mine.groups.list()
	clear_mine_gitlab_projects(gl_mine, my_groups)
	clone_groups(gl_mine, target_groups)

# ---- MAIN
if __name__ == "__main__":
	main()
