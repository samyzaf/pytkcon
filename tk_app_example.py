import sys
import tkinter as tk
from xcanvas import XCanvas
from pytkcon import TkConsole

# General template for creating a standard Application UI
# Just copy this code and replcae the methods to whatever you need
# The Main App window in this example is a Text window, but it can
# be replaced with whatever is needed

class TkApp(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, relief=tk.SUNKEN, bd=2)
    
        self.menubar = tk.Menu(self)
    
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(label="New", command=self.new_)
        menu.add_command(label="Open", command=self.open)
        menu.add_command(label="Exit", command=self.exit)
    
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=menu)
        menu.add_command(label="Cut", command=self.cut)
        menu.add_command(label="Copy", command=self.copy)
        menu.add_command(label="Paste", command=self.paste)
        menu.add_command(label="Clear ALL", command=self.clear)

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=menu)
        menu.add_command(label="About", command=self.about)
        menu.add_command(label="Help", command=self.help)

        self.master.config(menu=self.menubar)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = XCanvas(self, scrollbars=False, scalewidget=False, x_axis=0, y_axis=0, width=900, height=500, bg="cornsilk")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.tkcon = TkConsole(self, height=12)
        self.tkcon.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.tkcon.focus_set()

    def new_(self):
        tk.messagebox.showwarning(
            "Not implemented",
            "The 'new' method is not implemented yet"
        )

    def open(self):
        tk.messagebox.showwarning(
            "Not implemented",
            "The 'open' method is not implemented yet"
        )

    def exit(self):
        answer = tk.messagebox.askyesno(
            "Exit?",
            "Are you sure you want to exit?"
        )
        if answer:
            sys.exit(0)

    def clear(self):
        self.text.delete(1.0, tk.END)

    def cut(self):
        tk.messagebox.showwarning(
            "Not implemented",
            "The 'cut' method is not implemented yet"
        )

    def copy(self):
        tk.messagebox.showwarning(
            "Not implemented",
            "The 'copy' method is not implemented yet"
        )

    def paste(self):
        tk.messagebox.showwarning(
            "Not implemented",
            "The 'paste' method is not implemented yet"
        )

    def help(self):
        try:
            self.help_top.destroy()
        except:
            pass
        self.help_top = tk.Tk()
        self.help_top.wm_title('HELP WINDOW')
        t = tk.Text(self.help_top, font='Consolas 10 bold', width=80, height=24, background='cornsilk', foreground='blue')
        t.insert(tk.END, "Edit the help method:\nRead some help file and insert it here")
        t.pack(fill=tk.BOTH, expand=True)

    def about(self):
        tk.messagebox.showinfo(
            "About EDA Application",
            "Engineering Design Project\nEEE Depatment\nOrt Braude College"
        )


class StdoutRedirector(object):
    def __init__(self,text_widget):
        self.text = text_widget

    def write(self,string):
        self.text.insert('end', string)
        self.text.see('end')

class StderrRedirector(object):
    def __init__(self,text_widget):
        self.text = text_widget

    def write(self,string):
        self.text.insert('end', string)
        self.text.see('end')

def tk_app_example():
    root = tk.Tk()
    app = TkApp(root)
    app.pack()
    app.master.wm_title('EDA Design App')
    root.mainloop()

