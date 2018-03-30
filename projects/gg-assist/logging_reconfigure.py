#!/usr/bin/env python
import socket, sys, struct
import os, re, pprint
from pick import pick

# https://stackoverflow.com/questions/19617355/dynamically-changing-log-level-in-python-without-restarting-the-application

os.environ["TERM"] = "xterm-256color"
SCRIPT_NAME = os.path.basename(__file__)

def debugPrint(args):
	sys.stdout.write("[%s] " % SCRIPT_NAME)
	print (args)

def select_debug_option():
	title = 'Please choose debug option to set to gg-assist-wrapper:'
	options = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
	option, index = pick(options, title)
	return b"level=" + option.encode('UTF-8')

def get_current_debug_level(config_data):
	matches = []
	match = re.findall(b'(level=.+)', config_data, re.MULTILINE)
	pprint.pprint(match)
	for item in match:
		matches.append(item)
	return matches

def main():
	with open('logging.conf', 'rb') as f:
		data_to_send = f.read()

	debug_levels = get_current_debug_level(data_to_send)
	new_debug_level = select_debug_option()
	for level in debug_levels:
		print (new_debug_level)
		data_to_send = data_to_send.replace(level, new_debug_level)
	debugPrint(10*"*" + "New logging file looks like:" + 10*"*")
	print (data_to_send.decode('UTF-8'))
	debugPrint(10*"*" + "End" + 10*"*")

	HOST = 'localhost'
	PORT = 9999
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	debugPrint('connecting...')
	s.connect((HOST, PORT))
	debugPrint('sending config...')
	s.send(struct.pack('>L', len(data_to_send)))
	s.send(data_to_send)
	s.close()
	debugPrint('complete')

if __name__ == "__main__":
	main()
