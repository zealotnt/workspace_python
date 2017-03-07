import subprocess

# The standard input and output channels for the process started by call() are bound to the parent's input and output.
# That means the calling programm cannot capture the output of the command.
# Use check_output() to capture the output for later processing.
print 'Calling: ls -1'
output = subprocess.check_output(['ls', '-1'])
print 'Have %d bytes in output' % len(output)
print output

# This script runs a series of commands in a subshell.
# Messages are sent to standard output and standard error before the commands exit with an error code.
print 'Calling: echo to stdout; echo to stderr 1>&2; exit 0'
output = subprocess.check_output(
    'echo to stdout; echo to stderr 1>&2; exit 0',
    shell=True,
    )
print 'Have %d bytes in output' % len(output)
print output


# To prevent error messages from commands run through check_output() from being written to the console,
# set the stderr parameter to the constant STDOUT.
print 'Calling: echo to stdout; echo to stderr 1>&2; exit 0'
output = subprocess.check_output(
    'echo to stdout; echo to stderr 1>&2; exit 0',
    shell=True,
    stderr=subprocess.STDOUT,
    )
print 'Have %d bytes in output' % len(output)
print output
