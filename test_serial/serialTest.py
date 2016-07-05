#!/usr/bin/python
import time
import serial

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600
)

# ser.open()
ser.isOpen()


if ser.isOpen():
	print "Serial is open, write something in loop"
	while 1 :
	    ser.write("Hello" + '\r\n')
	    time.sleep(1)
	    while ser.inWaiting() > 0:
	        out += ser.read(1)

