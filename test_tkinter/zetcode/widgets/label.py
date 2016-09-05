#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode Tkinter tutorial

In this script, we use the Label
widget to show an image.

Author: Jan Bodnar
Last modified: November 2015
Website: www.zetcode.com
"""

from PIL import Image, ImageTk
from Tkinter import Tk, Frame, Label

import os
import inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

class Example(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.initUI()


    def initUI(self):

        self.parent.title("Label")

        self.img = Image.open(current_dir + "/../layout/mincol.jpg")
        tatras = ImageTk.PhotoImage(self.img)
        label = Label(self, image=tatras)

        # reference must be stored
        label.image = tatras

        label.pack()
        self.pack()


    def setGeometry(self):

        w, h = self.img.size
        self.parent.geometry(("%dx%d+300+300") % (w, h))


def main():

    root = Tk()
    ex = Example(root)
    ex.setGeometry()
    root.mainloop()


if __name__ == '__main__':
    main()