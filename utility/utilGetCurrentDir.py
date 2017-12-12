#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import inspect
CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(CURRENT_DIR)
