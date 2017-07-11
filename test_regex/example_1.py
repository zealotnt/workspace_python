#!/usr/bin/python

import re
import termcolor

def BeginSection(string):
	print termcolor.colored("\r\n\t" + string, 'green')

BeginSection("re.search example")
str = 'an example word:cat!! word:dog word:anything'
match = re.search(r'word:\w\w\w', str)
if match:
	print 'found', match.group()
else:
	print 'did not find'


BeginSection("re.findall example")
matchAll = re.findall(r'word:\w\w\w', str)
if match:
	print 'found', matchAll
else:
	print 'did not find'

BeginSection("re.findall and Groups")
str = 'purple -123@abc alice@google.com, blah monkey bob@abc.com blah dishwasher'
tuples = re.findall(r'([\w\.-]+)@([\w\.-]+)', str)
print tuples  ## [('alice', 'google.com'), ('bob', 'abc.com')]
for tuple in tuples:
	print tuple[0]  ## username
	print tuple[1]  ## host
