#!/usr/bin/python
import os
import platform
import re
import subprocess
import Tkinter as tk
import tkMessageBox as mbox
from ttk import Frame, Button, Style, Entry
import inspect
import thread
import signal
import time
import serial

_port = serial.Serial(port="COM45", baudrate=9600, timeout=0.1)
_port.write("Hello world")