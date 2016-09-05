'''
Here is an example of a new IntVar widget that uses an observer pattern
to control program flow.  Note that this sets a variable that broadcasts
to all relevant "listeners" that's its value has been changed.  The
variable's value is set by the widget but could be set by anything else
as well.  For example, if you have some other process that changes the
observable it could notify the widget to update to the new value as
well. - Brian Kelley
'''

from Tkinter import *
import Dialog

class Observable:
     def __init__(self, data):
         self.data = None
         self.callbacks = []

     def addCallback(self, func):
         """(function)-> add listeners"""
         self.callbacks.append(func)

     def set(self, data):
         """(data)->set the variable to be equal to data and
         call all listeners"""
         self.data = data
         for callback in self.callbacks:
             callback(data)

class ObservableIntVar(Frame):
     def __init__(self, master, **kw):
         apply(Frame.__init__, (self, master), kw)
         self._var = IntVar()
         b = Checkbutton(master,
                         variable=self._var,
                         command=self._setVar)
         b.pack()
         self._observable = Observable(self._var.get())

     def _setVar(self):
         self._observable.set(self._var.get())
         Dialog.Dialog(self,
                       title="Hello",
                       text="I'm set to %s"%self._var.get(),
                       bitmap=Dialog.DIALOG_ICON,
                       default=0, strings=('OK',))

     def add(self, callback):
         """(callback)->add a callback function that should be
         notified when the value of the IntVar changes"""
         self._observable.addCallback(callback)

if __name__ == "__main__":
     tk = Tk()
     ob = ObservableIntVar(tk)
     ob.pack()

     def callback(data):
         print "callback called with data =", data

     ob.add(callback)

     mainloop()