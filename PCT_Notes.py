import tkinter as tk
import tkinter.scrolledtext as tkst
import PCT_DB as pctdbs
import helper_ToolTip as ToolTip
from datetime import datetime, date, timedelta
import time
import logging

class PCT_Notes(tk.Frame):
    def __init__(self, master=None):
        self.master = master
        self.TasksDB_Handle = None
        self.NotesDB_Handle = pctdbs.PCT_NotesDB(self.master)
        self.holdnotetl = None
        self.butphoto = []
        self.but = []
        self.pct = None
        self.tid = None
        self.todaydt = str(date.today().isoformat())
    def editnote(self,pct,dbnhandle,dbthandle,keys):
        self.butphoto = []
        self.but = []
        self.notes = None
        self.pct = pct
        self.NotesDB_Handle = dbnhandle
        self.TasksDB_Handle = dbthandle
        self.tid = keys[0]
        prevnotesshow = int(self.TasksDB_Handle.get_config_item('PREVNOTESSHOW'))
        he = int(self.TasksDB_Handle.get_config_item('NOTESEDITROWS'))
        hv = int(self.TasksDB_Handle.get_config_item('NOTESVIEWROWS'))
        total_h = he + (hv * prevnotesshow)
        if total_h > 48:
            logging.warning("NOTES too many lines displayed " + str(total_h))
        w = int(self.TasksDB_Handle.get_config_item('NOTESWIDTH'))
        taskname = self.TasksDB_Handle.getTaskNamesp(self.tid)
        wtitle = 'Notes for ' + taskname[0] + ' ' + self.todaydt
        self.conn = self.NotesDB_Handle.conn_db('U',self.TasksDB_Handle)
        self.holdnotetl = tk.Toplevel(self.pct)
        self.holdnotetl.title(wtitle)
        self.holdnotetl.iconbitmap('digitalclock2.ico')
        self.butphoto.append(tk.PhotoImage(file='log_off.gif'))
        self.but.append(tk.Button(self.holdnotetl, image=self.butphoto[-1],
            command=lambda lltl = self.holdnotetl:self.pct.popupquit(lltl)))
        r = 0
        c = 0
        self.but[-1].grid(row=r, column=c)
        ToolTip.ToolTip(self.but[-1], anchor='e', text="Leave the window")
        c += 1
        self.butphoto.append(tk.PhotoImage(file='process.gif'))
        self.but.append(tk.Button(self.holdnotetl, image=self.butphoto[-1], command=self.process_note ))
        self.but[-1].grid(row=r, column=c)
        ToolTip.ToolTip(self.but[-1], anchor='e', text="Save the note")
        c = 0
        self.notes = self.NotesDB_Handle.getTaskNotes(self.tid, prevnotesshow)
        notee = self.notes[0]
        texte = None
        notev = self.notes[1]
        textv = []
        if len(notee) > 0:
            texte = notee[2]
        if len(notev) > 0:
            for nr in notev:
                textv.append(nr)
        self.textPad = tkst.ScrolledText(master=self.holdnotetl, width=w, height=he, wrap=tk.WORD)
        r += 1
        self.textPad.grid(row=r,column=c)
        self.textPad.focus_set()
        if texte != None:
            self.textPad.insert(tk.INSERT,texte)
        self.textPad.insert(tk.END, time.asctime(time.localtime()) + '\n')
        ToolTip.ToolTip(self.textPad, anchor='e', text="Enter the note update")
        viewPadL = []
        for ix,txt in enumerate(textv):
            viewPadL.append(tk.Label( self.holdnotetl, text=txt[1], anchor='w'))
            r += 1
            viewPadL[-1].grid(row=r+ix,column=c)
            viewPadL.append(tkst.ScrolledText(self.holdnotetl, width=w, height=hv, wrap=tk.WORD))
            r += 1
            viewPadL[-1].grid(row=r+ix,column=c)
            viewPadL[-1].insert(tk.INSERT,txt[2])
        # self.bind('<Control-c>', self.copy)
        # self.bind('<Control-x>', self.cut)
        # self.bind('<Control-v>', self.paste)
    def process_note(self):
        text = self.textPad.get('1.0',tk.END)
        self.pct.popupquit(self.holdnotetl)
        self.NotesDB_Handle.setTaskNote(self.tid, self.todaydt, text)
        self.NotesDB_Handle.release_db()
    def copy(self, event=None):
        self.clipboard_clear()
        text = self.get("sel.first", "sel.last")
        self.clipboard_append(text)
    
    def cut(self, event):
        self.copy()
        self.delete("sel.first", "sel.last")

    def paste(self, event):
        text = self.selection_get(selection='CLIPBOARD')
        self.insert('insert', text)
def rClicker(e):
    ''' right click context menu for all Tk Entry and Text widgets
    '''

    try:
        def rClick_Copy(e, apnd=0):
            e.widget.event_generate('<Control-c>')

        def rClick_Cut(e):
            e.widget.event_generate('<Control-x>')

        def rClick_Paste(e):
            e.widget.event_generate('<Control-v>')

        e.widget.focus()

        nclst=[
               (' Cut', lambda e=e: rClick_Cut(e)),
               (' Copy', lambda e=e: rClick_Copy(e)),
               (' Paste', lambda e=e: rClick_Paste(e)),
               ]

        rmenu = Menu(None, tearoff=0, takefocus=0)

        for (txt, cmd) in nclst:
            rmenu.add_command(label=txt, command=cmd)

        rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")

    except TclError:
        print( ' - rClick menu, something wrong')
        pass

    return "break"


def rClickbinder(r):

    try:
        for b in [ 'Text', 'Entry', 'Listbox', 'Label']: #
            r.bind_class(b, sequence='<Button-3>',
                         func=rClicker, add='')
    except TclError:
        print(' - rClickbinder, something wrong')
        pass


