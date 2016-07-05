#!/bin/env python
# -*- coding: cp1252 -*-
#==========================================================================
# (c) 2015 Texas Instruments
#--------------------------------------------------------------------------
# Project : Method and parameters for hardware interface adaptations
# File    : hw_interface.py
#--------------------------------------------------------------------------
# Redistribution and use of this file in source and binary forms, with
# or without modification, are permitted.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#==========================================================================

#==========================================================================
# IMPORTS
#==========================================================================
import sys
from config import *
import time
from time import sleep
# Imports related to Aardvark hardware interface
#from aardvark_rw import *
#from aardvark_py import *


#Import the i2c driver
from i2cBluefin import *

# Import the version number
from version import *


#==========================================================================
# GLOBALS
#==========================================================================
register = 0
#==========================================================================
# REGISTER CLASS DEFINITIONS
#==========================================================================


#==========================================================================
# FUNCTIONS
#==========================================================================

def hw_interface_init():
    # Initialize the I2C hardware interface based on settings in config.py

    print ' '
    print 'TPS65982/6 Debug Tool Version', TI_DEBUG_TOOL_VERSION
    print ' '
    
    if HW_INTERFACE == AARDVARK:
        #handle = init_aardvark(PORT, BITRATE, DEVICE_I2C_ADDR)
        print ' '
        print 'Hardware Interface: Aardvark on port', PORT
        print ' '
        return(handle)
    elif HW_INTERFACE == BLUEFIN:
	#TODO
	handle = mls_i2c_open_device(PORT, DEVICE_I2C_ADDR)
        print ' '
        print 'Hardware Interface: Bluefin on port', PORT
        print 'handle = ', handle
	return(handle)
    else:
        print 'Invalid hardware interface selected in config.py!' 
        sys.exit()

def hw_interface_close(handle):
    # Close the I2C hardware interface
    if HW_INTERFACE == AARDVARK:
        #aa_close(handle)
	print ' '
	print 'hw_interface_close'
	print ' '
    elif HW_INTERFACE == BLUEFIN:
	#TODO
	mls_i2c_close_device(handle)
	print ' '
        print 'hw_interface_close'
        print ' '
    else:
        print 'Invalid hardware interface selected in config.py!' 
        sys.exit()

def hw_i2c_write(handle, data_out):
    # Call the appropriate I2C hardware interface to write data
    # (write with normal start and stop conditions)
    if HW_INTERFACE == AARDVARK:
        #aa_i2c_write (handle, DEVICE_I2C_ADDR, AA_I2C_NO_FLAGS, data_out)
	print ' '
	print 'hw_i2c_write'
	print ' '
    elif HW_INTERFACE == BLUEFIN:
	#TODO

	#if 1

	#if 1
	#register = data_out[0]
	#__data_out = array('B', len(data_out) - 1)
	#for i in range(1, len(data_out)):
	#	__data_out[i - 1] = data_out[i]
	#elif 0
	#(register, _data_out) = data_out	
	#endif
	
	#handle.write_i2c_block_data(DEVICE_I2C_ADDR, register, __data_out)

	#else
	data_out = data_out.tolist();
	nbytes = len(data_out)
	mls_i2c_write_data(handle, len(data_out), data_out)
	#endif
    else:
        print 'Invalid hardware interface selected in config.py!' 
        sys.exit()

def hw_i2c_write_no_stop(handle, data_out):
    # Call the appropriate I2C hardware interface to write data
    # (write with start condition but no stop condition)
    if HW_INTERFACE == AARDVARK:
        #aa_i2c_write(handle, DEVICE_I2C_ADDR, AA_I2C_NO_STOP, data_out)
	print ' '
	print 'hw_i2c_write_no_stop'
	print ' '
    elif HW_INTERFACE == BLUEFIN:
	#TODO
	#To send register for reading data
	#In this function, data_out is register (see function "read_reg" in file "device_rw_py")
	data_out = data_out.tolist();
	register = data_out
	mls_i2c_write_data(handle, len(data_out), data_out)
    else:
        print 'Invalid hardware interface selected in config.py!' 
        sys.exit()

def hw_i2c_read(handle, length):
    # Call the appropriate I2C hardware interface to read data
    # (read with normal start and stop conditions)
    if HW_INTERFACE == AARDVARK:
        #(count, data_in) = aa_i2c_read(handle, DEVICE_I2C_ADDR, AA_I2C_NO_FLAGS, length)
        #if (count < 0):
        #    print "error: %s" % aa_status_string(count)
        #return(count, data_in)
	print ' '
	print 'hw_i2c_read'
	print ' '
    elif HW_INTERFACE == BLUEFIN:
	#TODO
	#To read data from a register, first, function "hw_i2c_write_no_stop" is called then function "hw_i2c_read"
	#data_in = handle.read_i2c_block_data(DEVICE_I2C_ADDR, register, length)
	#count = len(data_in)
	(data_in, count) = mls_i2c_read_data(handle, length)
	if(count < 1):
		print "error: read data"
	return(count, data_in)
    else:
        print 'Invalid hardware interface selected in config.py!' 
        sys.exit()

def hw_sleep_ms(time_msec):
    # Call the appropriate sleep timer
    if HW_INTERFACE == AARDVARK:
        #aa_sleep_ms(time_msec)
	print ' '
	print 'hw_sleep_ms'
	print ' '
    elif HW_INTERFACE == BLUEFIN:
	#TODO
	mls_i2c_sleep_ms(time_msec)
    else:
        print 'Invalid hardware interface selected in config.py!' 
        sys.exit()

#==========================================================================
# main
#==========================================================================
if __name__ == "__main__":
    print 'This file is a helper file for adapting the scripts to different'
    print 'hardware interfaces. It should be imported into a python'
    print 'environment or another script using:'
    print 'from hw_interface import *'
    sys.exit()
