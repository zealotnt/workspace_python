"""
Tkinter Color Vector Objects

Just the bare minimum to create re-sizable
and re-usable color icons in tkinter.
- Ron Adam
"""

import Tkinter as Tk
import math

def getregpoly(sides):
     """ Get points for a unit regular-polygon with n sides. """
     points = []
     ang = 2*math.pi / sides
     for i in range(sides):
         deg = (i+.5)*ang
         points.append(math.sin(deg)/2.0+.5)
         points.append(math.cos(deg)/2.0+.5)
     return points

def scale(points, scale):
     return [x*scale for x in points]

def move(points, x, y):
     xy = [x,y]*(len(points)//2)
     return [xy+coord for xy, coord in zip(xy,points)]

def translate(obj, x, y, zoom):
     p = scale(obj.points, obj.size)
     p = move(p, obj.x, obj.y)
     p = scale(p, zoom)
     return move(p, x, y)

def draw(obj, c, x=0 ,y=0, zoom=1):
     p = translate(obj, x, y, zoom)
     if obj.obj=='line':
         c.create_line( p, fill=obj.fill, width=obj.width,
                        arrow=obj.arrow )
     elif obj.obj=='rectangle':
         c.create_line( p, fill=obj.fill, outline=obj.outline,
                        width=obj.width)
     elif obj.obj=='polygon':
         c.create_polygon( p, fill=obj.fill, outline=obj.outline,
                           width=obj.width, smooth=obj.smooth )
     elif obj.obj=='text':
         size = int(obj.size*zoom)
         font = (obj.font,size,obj.style)
         c.create_text(p, text=obj.text, font=font, fill=obj.fill)
     elif obj.obj=='oval':
         c.create_oval( p, fill=obj.fill, outline=obj.outline,
                        width=obj.width )
     elif obj.obj=='arc':
         c.create_arc( p, start=obj.start, extent=obj.extent,
                       style=obj.style, fill=obj.fill,
                       outline=obj.outline, width=obj.width )

class Shape(object):
     size = 1
     x = y = 0
     def __init__(self, **kwds):
         self.__dict__.update(kwds)
     def __call__(self, *args, **kwds):
         for key in self.__dict__:
             if key not in kwds:
                 kwds[key] = self.__dict__[key]
         return self.__class__(*args, **kwds)
     def draw(self, c, x=0, y=0, scale=1.0):
         draw(self, c, x, y, scale)

class Group(list):
     obj = 'group'
     def __init__(self, *args, **kwds):
         self[:] = args
         self.__dict__.update(kwds)
     def __call__(self, *args, **kwds):
         args = self[:]+list(args)
         for key in self.__dict__:
             if key not in kwds:
                 # make copies
                 kwds[key] = self.__dict__[key]()
         return self.__class__(*args, **kwds)
     def draw(self, c, x=0, y=0, scale=1.0):
         for item in self:
             item.draw(c, x, y, scale)
         for key in self.__dict__:
             self.__dict__[key].draw(c, x, y, scale)

# base shapes.
text = Shape( obj='text', text='', fill='black', width=0,
               font='', style='', points=[0,0] )
line = Shape( obj='line', arrow='none', fill='black',
               smooth='false', width=1, points=[0,0,1,0])
rectangle = Shape( obj='rectangle', fill='', outline='black',
                    width=1, points=[0,0,1,.5])
polygon = Shape( obj='polygon', fill='grey', outline='',
                  width=0, points=[0,0], smooth='false' )
oval = Shape( obj='oval', fill='grey', outline='',
               width=0, points=[0,0,1,.75] )
arc = Shape( obj='arc', fill='grey', outline='', width=0,
              style='arc', start='0', extent='90',
              points=[0,0,1,1])

# shape variations
chord = arc(style='chord')
pie = arc(style='pieslice')
circle = oval(points=[0,0,1,1])
square = rectangle(points=[0,0,1,1])
triangle = polygon( points=getregpoly(3))
octagon = polygon( points=getregpoly(8))

# CAUTION ICON
caution = Group(
     triangle(x=6, y=5, size=75),
     triangle(size=75, fill='yellow'),
     txt = text( text='!',
                 x=38, y=32, size=30,
                 font='times', style='bold') )

# ERROR ICON
circlepart = chord( x=15, y=15, size=25, fill='red',
                     start='140', extent='155' )
error = Group(
     octagon(x=6, y=5, size=56),
     octagon(size=56, fill='red'),
     circle(x=9, y=9, size=37, fill='white'),
     circlepart(),
     circlepart(start='320') )

# QUESTION & INFO ICONS
bubbletip = polygon(points=[34,42,60,56,50,38])
question = Group(
     bubbletip(x=6, y=5),
     oval(x=6, y=5, size=60),
     bubbletip(fill='lightblue'),
     oval(size=60, fill='lightblue'),
     txt = text( text='?',
                 x=31, y=22, size=28,
                 font='times', style='bold' ) )
info = question()
info.txt.text = 'i'

if __name__ == '__main__':
     root = Tk.Tk()
     root.title('Resizable Shapes')
     c = Tk.Canvas(root)

     caution.draw(c,40,20,.5)
     error.draw(c,120,20,1)
     question.draw(c,210,20,2)
     info.draw(c,50,100)

     logo = caution()  # get a copy
     logo.txt = text( text='&', fill='#00bb44',
                        x=39, y=34, size=30 )
     logo.draw(c,135,110,1.3)

     message = text( text="What's Your Size?",
                     size=15, fill='white' )
     Group( message( x=1, y=1, fill='grey30'),
            message() ).draw(c,190,235,2)

     line( width=3, fill='darkgrey', arrow='both'
           ).draw(c,20,205,336)

     c.pack()
     root.mainloop() 