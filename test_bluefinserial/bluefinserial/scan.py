#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# src/scan.py

""" Serial port Scanner

:Summary: Serial port Scanner
:Author: Grégory Romé - gregory.rome@maxim-ic.com
:Organization: Maxim Integrated Products
:Copyright: Copyright © 2009, Maxim Integrated Products
:License: BSD License - http://www.opensource.org/licenses/bsd-license.php

"""

import glob
import os

import serial


def scan():
    """
    Return a name list of available serial ports
    """

    available = []

    if os.name == 'posix':
        available = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    else:
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append(s.portstr)
                s.close()   # explicit close 'cause of delayed GC in java
            except serial.SerialException:
                pass
    return available

if __name__ == '__main__':
    print scan()
