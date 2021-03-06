#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode Tkinter tutorial

In this program, we create a toolbar.

Author: Jan Bodnar
Last modified: November 2015
Website: www.zetcode.com
"""

from PIL import Image, ImageTk
from Tkinter import Tk, Frame, Menu
from Tkinter import Button, LEFT, TOP, X, FLAT, RAISED

import os
import inspect
CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/'
IMG_DIR = CURRENT_DIR + "../../../img/"

class Example(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.initUI()


    def initUI(self):

        self.parent.title("Toolbar")

        menubar = Menu(self.parent)
        self.fileMenu = Menu(self.parent, tearoff=0)
        self.fileMenu.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="File", menu=self.fileMenu)

        toolbar = Frame(self.parent, bd=1, relief=RAISED)

        self.img = Image.open(IMG_DIR + "exit.png")
        cropped = self.img.resize((25, 25), Image.ANTIALIAS)
        eimg = ImageTk.PhotoImage(cropped)

        exitButton = Button(toolbar, image=eimg, relief=FLAT,
            command=self.quit)
        exitButton.image = eimg
        exitButton.pack(side=LEFT, padx=2, pady=2)

        toolbar.pack(side=TOP, fill=X)
        self.parent.config(menu=menubar)
        self.pack()


    def onExit(self):
        self.quit()


def main():

    root = Tk()
    root.geometry("250x150+300+300")
    app = Example(root)
    root.mainloop()


if __name__ == '__main__':
    main()
