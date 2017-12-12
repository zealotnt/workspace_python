#!/usr/bin/python3
# [Ref](http://blog.programster.org/ubuntu-16-04-gnome-terminal-double-click-selection/)
# [Ref-1](https://askubuntu.com/questions/8413/can-i-specify-what-characters-set-the-double-click-selection-boundary-in-gnome-t)
# [Ref-2](https://github.com/ab/ubuntu-wart-removal/blob/master/gnome-terminal-word-separators.sh)
import subprocess

command = ["dconf", "list", "/org/gnome/terminal/legacy/profiles:/"]
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

profiles = result.stdout.split('\n')

for profileString in profiles:
    if profileString.startswith(":"):
        changeCmdPart = "/org/gnome/terminal/legacy/profiles:/" + profileString + "word-char-exceptions"
        changeCmd = ["dconf", "write", changeCmdPart, '@ms "-#%&+,./:=?@_~"']
        subprocess.run(changeCmd)

print("done!")
