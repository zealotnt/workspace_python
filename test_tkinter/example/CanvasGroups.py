# Andrew McVeigh
from Tkinter import *
from Canvas import *
from time import time

# define a mouse handling class
class MouseHandler:
    group = lastX = lastY = 0

    def __init__(self, group):
        self.group = group
        group.bind('<1>', self.click)
        group.bind('<B1-Motion>', self.move)

    def click(self, event):
        self.lastX = event.x
        self.lastY = event.y

    def move(self, event):
        self.group.move(event.x - self.lastX, event.y - self.lastY)
        self.click(event)

class CanvasDemo:

    colors = ["pink", "grey", "yellow", "green", "red", "purple", "cyan",
            "pink", "grey", "yellow", "green", "red", "purple", "cyan",
            "pink", "grey", "yellow", "green", "red", "purple", "cyan"]
    layers = 5
    root = canvas = groups = None

    def __init__(self, root):
        self.root = root

        # make a frame and a canvas and some buttons
        frame = Frame(self.root)
        frame.pack(fill=X)
        label = Label(frame, text="Canvas test")
        label.pack()
        self.canvas = Canvas(frame, bg="grey", width=600, height=600)
        self.canvas.pack()
        cmd = Button(frame, text="Scale", command=self.scale)
        cmd.pack()
        self.groups = []
        for i in range(self.layers):
            self.groups.append(Group(self.canvas))

        # time the creation of the rectangles
        start = time()
        self.makeShapes()
        print "Took ", time() - start, " seconds to make", self.layers,"layers"

    def makeShapes(self):
        # make 100 rectangles
        for group in range(self.layers):
            actual = self.groups[group]
            MouseHandler(actual)
            for i1 in range(10):
                for i2 in range(10):
                    makeRectangle(self.canvas, actual, i1*40+10+group*20,
                            i2*40+10+group*5,
                            35, 35, self.colors[group], 2)

    def scale(self):
        for group in self.groups:
            group.scale(0, 0, 1.1, 1.1)


def makeRectangle(canvas, group, left, top, width, height, color,thickness=2):
    rect = Rectangle(canvas, left,top, left+width,top+height,
                     fill=color, width=thickness)
    line = Line(canvas, left,top+height, left,top, left+width,top,
                width=thickness, fill="white")
    text = CanvasText(canvas, left+17, top+10, text="Hello!",fill="white")
    for shape in [rect, line, text]:
        group.addtag_withtag(shape)


if __name__ == '__main__':
    print "Canvas Demonstration"
    root = Tk()
    demo = CanvasDemo(root)
    root.mainloop()