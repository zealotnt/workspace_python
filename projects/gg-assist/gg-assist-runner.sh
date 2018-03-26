#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

start_gg_assistant() {
	source ~/gg-assistant/env/bin/activate
	cd $DIR
	python ~/gg-assistant/gg-assist-lib-wrapper.py &
}

if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
	exit 0
else
	case $(ps -o comm= -p $PPID) in
		sshd|*/sshd) exit 0;;
	esac
fi

start_gg_assistant
