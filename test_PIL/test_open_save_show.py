from PIL import Image
from PIL import ImageFilter
import sys

import os
import inspect
CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

PIL_Version = Image.VERSION
print "Image library version = " + PIL_Version

i = Image.open(CURRENT_DIR + r"\..\test_tkinter\zetcode\layout\mincol.jpg")
i.show()

im = i.filter(ImageFilter.EMBOSS)
im.save("output.jpg")
im.show()
