from .pytkcon import TkConsole

def tk_console(**opt):
    opt.setdefault('width', 100)
    opt.setdefault('height', 30)
    opt.setdefault('background', 'white')
    opt.setdefault('foreground', 'DarkGreen')
    opt.setdefault('font', ('Consolas', 10, 'normal'))
    tkcon = TkConsole(**opt)
    top = tkcon.winfo_toplevel()
    top.title('TkConsole Topelevel window')
    top.geometry("+300+250")
    tkcon.pack()
    tkcon.focus_set()
    tkcon.master.mainloop()

