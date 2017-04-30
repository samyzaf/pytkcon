import sys, os, rlcompleter
import tkinter
import easygui
from tkinter.scrolledtext import ScrolledText
from tkinter import TOP, RIGHT, LEFT, Y, BOTH, VERTICAL, HORIZONTAL, N, S, E, W, SUNKEN, END, INSERT, SEL, SEL_FIRST, SEL_LAST
from threading import Lock

welcome_text = """\
Welcome to a Python Interactive Console
Use <Shift-Enter> for multi-line commands
Use <Tab> for autocomplete
"""

class TkConsole(ScrolledText):
    "Tk console widget which can be easily embedded withing tkinter widgets"
    def __init__(self, master=None, **opt):
        opt.setdefault('width', 80)
        opt.setdefault('height', 24)
        opt.setdefault('background', 'gray92')   # 'cornsilk', 'FloralWhite'
        opt.setdefault('foreground', 'DarkGreen')
        opt.setdefault('font', ('Consolas', 9, 'normal'))
        self.initfile = opt.pop('initfile', None) 
        self.history = []
        self.complete = rlcompleter.Completer(globals()).complete
        self.write_lock = Lock()

        ScrolledText.__init__(self, master, **opt)
        self.pack(side=TOP, fill=BOTH, expand=True)
        self.text_init(opt)
        self.bindings()
        sys.stdout = StdoutRedirector(self)
        sys.stderr = StderrRedirector(self)
        self.prompt()
        self.write_end(welcome_text, ('welcome',))
        self.focus_set()
        self.run_initfile()

    def text_init(self, opt):
        prompt_font = opt['font'][0:2] + ('bold',)
        self._prompt = ">>> "
        self.tag_config('prompt', font=prompt_font, foreground='maroon')
        self.tag_config('output', foreground='DarkGreen')
        self.tag_config('error', foreground='red')
        self.tag_config('welcome', foreground='DarkGreen')
        self.tag_config('cmd', foreground='tan4')

    def bindings(self):
        self.bind("<Return>", self.on_Return)
        #self.bind("<KeyRelease-Return>", self.on_Return)
        self.bind("<Shift-KeyRelease-Return>", self.on_Return)
        self.bind("<KeyRelease-Up>", self.on_Up)
        self.bind("<BackSpace>", self.on_BackSpace)
        self.bind("<Delete>", self.on_Delete)
        self.bind("<Tab>", self.on_Tab)
        self.bind("<Key>", self.on_Key)
        self.bind("<Control-l>", self.clear)
        self.bind("<Enter>", self.focus)

    def run(self, cmd=None):
        #line,char = self.index('end').split('.')
        #last_line = self.index('end').split('.')[0]
        #print(self.index('limit'), self.index(INSERT))
        self.tag_add('cmd', 'limit', "%s-1c" % INSERT)
        if cmd is None:
            cmd = self.get('limit', END).lstrip()
            #print(cmd)
            self.history.append(cmd)
        self.eval(cmd)
        self.prompt()

    def eval(self, cmd):
        try:
            compile(cmd, '<stdin>', 'eval')
            try:
                e = eval(cmd, globals())
                #e = eval(cmd)
                #self.write(END, '\n')
                if e is not None:
                    self.write(END, e, ('output',))
            except Exception as err:
                self.write(END, "ERROR:\n%s\n" % err, ('error',))
        except SyntaxError:
            try:
                exec(cmd, globals())
            except Exception as emsg:
                self.write(END, "ERROR:\n%s\n" % emsg, ('error',))

    def prompt(self):
        #self.tag_delete('prompt')
        #self.tag_remove('prompt', 1.0, END)
        if len(get_last_line(self)):
            self.write(END, '\n')
        self.write(END, self._prompt, ('prompt',))
        self.mark_set(INSERT, END)
        #self.mark_set('limit', INSERT)
        self.mark_set('limit', '%s-1c' % INSERT)
        self.see(END)

    def write(self, index, chars, *args):
        self.write_lock.acquire()
        self.insert(index, chars, *args)
        #self.see(index)
        self.write_lock.release()

    def write_end(self, txt, tag):
        l1,c1 = index_to_tuple(self, "%s-1c" % END)
        l2,c2 = index_to_tuple(self, 'limit')
        if l1 == l2:
            self.write('limit-3c', txt, (tag,))
        else:
            self.write('end', txt, (tag,))
        self.see('end')

    def writeline(self, txt, tag):
        txt += '\n'
        self.write_end(txt, tag)

    def on_BackSpace(self, event=None):
        #print(self.get('1.0', 'limit'))
        #print(event.keysym)
        #print(self.mark_names())
        if self.tag_nextrange(SEL, '1.0', END) and self.compare(SEL_FIRST, '>=', 'limit'):
            self.delete(SEL_FIRST, SEL_LAST)
        elif self.compare(INSERT, '!=', '1.0') and self.compare(INSERT, '>', 'limit+1c'):
            self.delete('%s-1c' % INSERT)
            self.see(INSERT)
        return "break"

    def on_Delete(self, event=None):
        #print(event.keysym)
        #print(self.mark_names())
        if self.tag_nextrange(SEL, '1.0', END) and self.compare(SEL_FIRST, '>=', 'limit'):
            self.delete(SEL_FIRST, SEL_LAST)
        elif self.compare(INSERT, '>', 'limit+1c'):
            self.delete('%s-1c' % INSERT)
            self.see(INSERT)
        return "break"

    def on_Return(self, event=None):
        modifiers = event_modifiers(event)
        #print(event.keysym, modifiers)
        if self.compare(INSERT, '<', 'limit'):
            if 'Shift' in modifiers: return "break"
            if 'Control' in modifiers: return "break"
            cmd = self.get_cur_cmd()
            #print("cmd=", cmd, "limit=", self.index('limit'))
            if cmd:
                self.insert_cmd(cmd)
                return "break"
        else:
            if 'Shift' in modifiers or 'Control' in modifiers:
                return
            self.mark_set(INSERT, END)
            self.write(END, '\n')
            self.run()
        return "break"

    def on_Key(self, event=None):
        modifiers = event_modifiers(event)
        special = ['x', 'v', 'd', 'h', 'i', 'k', 'o']
        if 'Control' in modifiers or 'Alt' in modifiers:
            if self.compare(INSERT, '<=', 'limit'):
                if event.keysym in special:
                    return "break"
                return
        elif self.compare(INSERT, '<=', 'limit'):
            if event.char:
                return "break"

    def on_Up(self, event=None):
        pos = self.tag_prevrange('cmd', INSERT, '1.0')
        if not pos:
            return
        idx1,idx2 = pos
        l1,c1 = index_to_tuple(self, idx1)
        l2,c2 = index_to_tuple(self, idx2)
        #l,c = index_to_tuple(self, INSERT)
        idx = str(l1) + '.end'
        self.mark_set(INSERT, idx)
        self.see(INSERT)
        #self.prompt()
        return

    def on_Tab(self, event):
        if self.compare(INSERT, '<', 'limit'):
            return "break"
        cmd = self.get('limit', END).strip()
        completions = []
        i = 0
        done = dict()
        while True:
            c = self.complete(cmd, i)
            if c is None or c in done:
                break
            done[c] = None
            completions.append(c)
            i += 1
        if completions:
            if len(completions) == 1:
                self.insert_cmd(completions[0])
            else:
                self._print(display_list(completions))
                if cmd:
                    self.insert_cmd(cmd)
        return "break"

    def insert_cmd(self, cmd):
        self.delete('limit+1c', END)
        self.write(END, cmd, ('cmd',))
        self.mark_set(INSERT, END)
        self.see(END)

    def get_cur_cmd(self):
        ranges = self.tag_ranges('cmd')
        ins = "%s-1c" % INSERT
        for i in range(0, len(ranges), 2):
            start = ranges[i]
            stop = ranges[i+1]
            #print(repr(self.get(start, stop)))
            #print(index_to_tuple(self, start), index_to_tuple(self, ins), index_to_tuple(self, stop))
            if self.compare(start, '<=', ins) and self.compare(ins, '<=', stop):
                return self.get(start, stop).lstrip()
        return ""

    def _print(self, txt):
        self.tag_add('cmd', 'limit', "%s-1c" % END)
        self.write(END, '\n')
        self.write(END, txt)
        self.prompt()
        #self.insert_cmd(cmd)
    
    def clear(self, event=None):
        self.delete(1.0, END)
        self.prompt()

    def focus(self, event=None):
        self.focus_set()

    def run_initfile(self):
        if self.initfile is None:
            return 0
        if not os.path.exists(self.initfile):
            self.writeline("Initialization file %s does not exist!" % (self.initfile,), 'error')
            return 1
        with open(self.initfile) as f:
            code = compile(f.read(), self.initfile, 'exec')
            try:
                exec(code, globals())
                self.writeline("Initialization file %s was successfuly executed" % (self.initfile,), 'output')
            except Exception as e:
                self.writeline("Failed to execute initialization file %s:" % (self.initfile,), 'error')
                self.writeline(e.message, 'error')
                return 2
        return 0

    def none(self, event=None):
        pass
        #return "continue"
        #return "break"

#-------------------------------------------------------------------------

class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text = text_widget

    def write(self, string):
        sys.__stdout__.write(string)
        l1,c1 = index_to_tuple(self.text, "%s-1c" % END)
        l2,c2 = index_to_tuple(self.text, 'limit')
        if l1 == l2:
            self.text.write('limit-3c', string)
        else:
            self.text.write('end', string)
        self.text.see('end')
        #self.text.master.update()

    def writelines(self, lines):
        sys.__stdout__.writelines(lines)
        for line in lines:
            self.text.write(line)

    def flush(self):
        #self.text.master.update()
        sys.__stdout__.flush()


class StderrRedirector(object):
    def __init__(self, text_widget):
        self.text = text_widget

    def write(self, string):
        sys.__stderr__.write(string)
        l1,c1 = index_to_tuple(self.text, "%s-1c" % END)
        l2,c2 = index_to_tuple(self.text, 'limit')
        if l1 == l2:
            self.text.write('limit-3c', string)
        else:
            self.text.write('end', string)
        self.text.see('end')
        #self.text.master.update()

    def writelines(self, lines):
        sys.__stderr__.writelines(lines)
        for line in lines:
            self.text.write(line)

    def flush(self):
        #self.text.master.update()
        sys.__stderr__.flush()


#class StdinRedirector(object):
#    def __init__(self,text_widget):
#        self.text = text_widget
#
#    def readline(self):
#        line = self.ifh.readline()
#        if line:
#            self.ofh.write(line)
#        return line

def event_modifiers(event):
    modifiers = []
    if event.state & 0x00001:
        modifiers.append('Shift')
    if event.state & 0x00004:
        modifiers.append('Control')
    if event.state & 0x20000:
        modifiers.append('Alt')
    if event.state & 0x00002:
        modifiers.append('Caps_Lock')
    if event.state & 0x00400:
        modifiers.append('Right_Down')
    if event.state & 0x00200:
        modifiers.append('Middle_Down')
    #print(modifiers)
    return modifiers

def index_to_tuple(text, index):
    return tuple(map(int, text.index(index).split(".")))

def tuple_to_index(t):
    l,c = t
    return str(l) + '.' + str(c)

def get_last_line(text):
    l,c = index_to_tuple(text, END)
    l -= 1
    start = tuple_to_index((l,0))
    end = str(l) + ".end"
    return text.get(start, end)

#def display_list(L):
#    txt = ""
#    n = 0
#    for e in L:
#        e = str(e)
#        if n > 80:
#            e += '\n'
#            n = 0
#        else:
#            e += '\t'
#            n += len(e)
#        txt += e
#    #txt += '\n'
#    return txt

def display_list(L):
    txt = ""
    line = ""
    n = max([len(w) for w in L])
    n = max(n,18) + 2
    fmt =  "%-" + str(n) + "s"
    for e in sorted(L):
        e = str(e)
        if len(line) > 60:
            txt += line + '\n'
            line = ""
        else:
            line += fmt % e
    if len(line):
        txt += line
        #txt += '\n'
    return txt

def raw_input(prompt=""):
    if prompt == "":
        prompt = "Input:"
    return easygui.enterbox(prompt, "Raw input", None)



