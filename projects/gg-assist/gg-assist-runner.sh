#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

start_gg_assistant() {
	source ~/gg-assistant/env/bin/activate
	cd $DIR
	python ~/gg-assistant/gg-assist-lib-wrapper.py &
}

# https://serverfault.com/questions/187712/how-to-determine-if-im-logged-in-via-ssh
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
	exit 0
else
	case $(ps -o comm= -p $PPID) in
		sshd|*/sshd) exit 0;;
	esac
fi

# https://unix.stackexchange.com/questions/270272/how-to-get-the-tty-in-which-bash-is-running/270372
# TODO: only accept running app at ttymxc0
if [[ $(tty) = "/dev/ttymxc0" ]]; then
	start_gg_assistant
fi
