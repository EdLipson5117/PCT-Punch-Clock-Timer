import tkinter as tk
import tkinter.scrolledtext as tkst
import PCT_PunchClock as punchclock
import PCT_DB as PCT_DB
import helper_ToolTip as ToolTip
import helper_datepicker as datepicker
from datetime import datetime, date, timedelta
import math
import os
import logging
import textwrap


class PCT_History(tk.Frame):

    def __init__(self, master=None):
        self.master = master
        self.DB_Handle = None
        self.NotesDB_Handle = None
        self.pct_Handle = None
        self.history_tl = None
        self.quitphoto = None
        self.pct = None
        self.datedhandle = None
        self.dt = None
        self.listshowed = False
        self.tasklistrows = []
        self.lstb = None
        self.prcb = None
        self.valdict = {}
        self.buildvaldict()
        self.etllists = []
        self.etlists = []
        self.edtfld = []
        self.lrow = None
        self.active_task_index = None

    def historical_edit(self, pct, dbh):
        self.listshowed = False
        self.lrow = None
        self.pct = pct
        self.DB_Handle = dbh
        self.pct_Handle = pct
        self.NotesDB_Handle = self.pct_Handle.get_notesDB_handle()
        self.history_tl = tk.Toplevel(self.pct)
        self.history_tl.iconbitmap('digitalclock2.ico')
        self.history_tl.title("Edit a specific date's time'")
        self.qphoto = tk.PhotoImage(file='log_off.gif')
        self.qb = tk.Button(self.history_tl, image=self.qphoto,
                            command=lambda lltl=self.history_tl: punchclock.PCT_PunchClock.popupquit(self.pct, lltl))
        self.qb.grid(row=0, column=0)
        ToolTip.ToolTip(self.qb, anchor='e', text="Leave the window")
        self.calphoto = tk.PhotoImage(file='Google-Calendar-icon.gif')
        self.calb = tk.Button(self.history_tl, image=self.calphoto,
                              command=self.datepicker_pop)
        self.calb.grid(row=0, column=1)
        ToolTip.ToolTip(
            self.calb, anchor='e', text="Use a Calendar Widget to select the date")
        self.lstphoto = tk.PhotoImage(file='list.gif')
        self.lstb = tk.Button(self.history_tl, image=self.lstphoto, state=tk.ACTIVE,  # testing tk.DISABLED,
                              command=lambda: self.show_a_dates_tasks())
        self.lstb.grid(row=0, column=2)
        ToolTip.ToolTip(
            self.lstb, anchor='e', text="Show the tasks for the date")
        self.datedhandle = datepicker.DateData()
        self.dt = self.datedhandle.getDateDatadisp()
        dl = tk.Label(self.history_tl, text="Date", anchor='e', width=10)
        dl.grid(row=1, column=1)
        dl = tk.Label(
            self.history_tl, textvariable=self.dt, width=23, anchor='w')
        dl.grid(row=1, column=2)

    def datepicker_pop(self):
        # print("datepicker_pop")
        if self.lrow != None:
            [lb2, lb4, lb5] = self.etllists[0]
            end = self.lrow - 2
            lb2.delete(0, end)
            lb4.delete(0, end)
            lb5.delete(0, end)
            self.lrow = None
        self.datepicker_tl = tk.Toplevel(self.master)
        self.datepicker_tl.iconbitmap('digitalclock2.ico')
        ldate = datepicker.Calendar(self.datepicker_tl, self.datedhandle)
        self.lstb.config(state=tk.ACTIVE)
        if self.listshowed == True:
            self.tasklistrows = []
            self.listshowed = False
        self.datepicker_tl.grab_set()

    def show_a_dates_tasks(self):
        # print("show_a_dates_tasks")
        self.listshowed = True
        self.active_task_index = None
        self.lstb.config(state=tk.DISABLED)
        self.etllists = [
            None, None, None, None, None, None, None, self.pct_Handle, self.DB_Handle]
        svardt = self.dt.get()
        dt = svardt[0:10]
        yr = dt[0:4]
        tasks = PCT_DB.PCT_TimeDB.get_history_tasks(self.DB_Handle, dt, yr)
        tnwidth = PCT_DB.PCT_TimeDB.get_max_but_len(self.DB_Handle) * 2
        vsb = tk.Scrollbar(
            self.history_tl, orient="vertical", command=self.etl_OnVsb)
        self.etllists[1] = vsb
        cl2 = tk.Label(self.history_tl, text='Project Task')
        cl4 = tk.Label(self.history_tl, text='Time')
        cl5 = tk.Label(self.history_tl, text='Exists')
        self.lrow = 2
        cl2.grid(row=self.lrow, column=0)
        cl4.grid(row=self.lrow, column=1)
        cl5.grid(row=self.lrow, column=2)
        lb2 = tk.Listbox(self.history_tl, yscrollcommand=vsb.set,
                         exportselection=1, width=tnwidth, selectmode=tk.SINGLE)
        ToolTip.ToolTip(
            lb2, anchor='e', text="Select the task to edit by clicking on the name")
        lb4 = tk.Listbox(self.history_tl, yscrollcommand=vsb.set,
                         exportselection=0, takefocus=0, relief=tk.FLAT)
        lb5 = tk.Listbox(self.history_tl, yscrollcommand=vsb.set,
                         exportselection=0, takefocus=0, relief=tk.FLAT)
        self.lrow += 1
        vsb.grid(row=self.lrow, column=4, sticky=tk.N + tk.S)
        lb2.grid(row=self.lrow, column=0)
        lb4.grid(row=self.lrow, column=1)
        lb5.grid(row=self.lrow, column=2)
        lb2.bind("<MouseWheel>", self.etl_OnMouseWheel)
        lb2.bind('<ButtonRelease-1>', self.etl_process_sel)
        lb4.bind("<MouseWheel>", self.etl_OnMouseWheel)
        lb5.bind("<MouseWheel>", self.etl_OnMouseWheel)
        ttlist = []
        #    0              1              2              3                   4             5              6
        # TT.TASKTIME_ID, T.TASK_ID, TT.TASK_TIME_NO, TT.TASK_TIME_DT, TT.TASK_TYPE_CD, T.TASK_NM, T.TASK_PROJ_NM
        for ix, task in enumerate(tasks):
            self.lrow += 1
            nm = task[6] + ' ' + task[5]
            lb2.insert("end", "%s" % nm)
            if task[2] != None:
                tm = int(int(task[2]) / 60)
            else:
                tm = 0
            tm = str(tm) if tm > 0 else 'None'
            lb4.insert("end", "%s" % tm)
            used = 'Yes' if task[0] != None else 'No'
            lb5.insert("end", "%s" % used)
            ttlist.append(task)
        self.etllists[0] = [lb2, lb4, lb5]
        self.etllists[5] = [cl2, cl4, cl5]
        self.etllists[6] = ttlist

    def etl_OnVsb(self, *args):
        for etll in self.etllists[0]:
            etll.yview(*args)

    def etl_OnMouseWheel(self, event):
        for etll in self.etllists[0]:
            etll.yview("scroll", event.delta, "units")
        # this prevents default bindings from firing, which
        # would end up scrolling the widget twice
        return "break"

    def etl_process_sel(self, event):
        ix = event.widget.curselection()[0]
        self.active_task_index = ix
        tt = self.etllists[6][ix]
        self.edit_tasktime(tt)

    def edit_tasktime(self, tt):
        #    0              1              2              3                   4             5              6
        # TT.TASKTIME_ID, T.TASK_ID, TT.TASK_TIME_NO, TT.TASK_TIME_DT, TT.TASK_TYPE_CD, T.TASK_NM, T.TASK_PROJ_NM
        self.etlists = [None, None, None, None, None, None, [], [], [], [], []]
        holdettl = tk.Toplevel(self.history_tl)
        holdettl.title("Edit Task")
        holdettl.iconbitmap('digitalclock2.ico')
        self.etlists[0] = holdettl
        self.etlists[4] = tt
        # 0 is toplevel
        # 1 is button image, button logoff
        # 2 is button image, button update/add
        # 3 is button image, button delete (misc)
        # 4 is list of attributes
        # 5 is has notes, so no delete possible
        # 6 edit string vars list
        # 7 validate cmd string vars list
        # 8 invalid cmd string vars list
        # 9 validation option
        # 10 edit fileds
        quitphoto = tk.PhotoImage(file='log_off.gif')
        etqb = tk.Button(
            holdettl, image=quitphoto, anchor='w', command=self.edit_task_quit)
        etqb.grid(row=0, column=0)
        self.etlists[1] = [quitphoto, etqb]
        ToolTip.ToolTip(etqb, anchor='e', text="Leave the window")
        processphoto = tk.PhotoImage(file='process.gif')
        self.edtfldprocessbut = tk.Button(
            holdettl, image=processphoto, anchor='e', command=self.edit_task_update)
        self.edtfldprocessbut.grid(row=0, column=1)
        self.edtfldprocessbut.config(default=tk.DISABLED, state=tk.DISABLED)
        self.etlists[2] = [processphoto, self.edtfldprocessbut]
        ToolTip.ToolTip(
            self.edtfldprocessbut, anchor='e', text="Add/update the changes")
        deletephoto = tk.PhotoImage(file='delete.gif')
        self.deletebut = tk.Button(
            holdettl, image=deletephoto, anchor='e', command=self.delete_task)
        self.deletebut.grid(row=0, column=2)
        self.deletebut.config(default=tk.DISABLED, state=tk.DISABLED)
        self.etlists[3] = [deletephoto, self.deletebut]
        ToolTip.ToolTip(
            self.edtfldprocessbut, anchor='e', text="Delete the task")
        if tt[3] != None:
            self.NotesDB_Handle.conn_db('R', self.DB_Handle)
            [notes, __] = self.NotesDB_Handle.getTaskNotes(tt[1], 1, tt[3])
            self.NotesDB_Handle.release_db()
            self.etlists[5] = notes
        twidth = 25
        self.etlists[6] = []
        self.etlists[7] = []
        self.etlists[8] = []
        self.etlists[9] = []
        self.etlists[10] = []
        self.add_field(1, "Project Name", twidth, len(tt[6]), 'D1', tt[6], None,
                       "The name of the project from PPM")
        self.add_field(2, "Task Name", twidth, len(tt[5]), 'D1', tt[5], None,
                       "The name of the task from PPM")
        if tt[2] == None:
            time = 0
        else:
            time = int(tt[2])
        self.add_field(3, "Task time", twidth, 5, 'E', int(time / 60), 'NT',
                       "Time in minutes")
        self.etlists[10][2][0].focus_set()
        if self.etlists[5] == None or self.etlists[5] == []:
            notes = "None"
            self.add_field(4, "Notes", twidth, 5, 'D1', notes, None,
                           "The name of the task from PPM")
            if tt[0] != None:
                self.deletebut.config(state=tk.ACTIVE)
        else:
            notes = self.etlists[5][2]
            self.add_field(4, "Notes", twidth, 35, 'DA', notes, None,
                           "The notes for the task on this date")

    def edit_task_quit(self):
        self.etlists[0].destroy()

    def edit_task_update(self):
        time = int(self.etlists[6][2].get()) * 60
        tt = self.etllists[6][self.active_task_index]
        tid = tt[1]
        tcd = tt[4]
        dt = self.dt.get()[0:10]
        #    0              1              2              3                   4             5              6
        # TT.TASKTIME_ID, T.TASK_ID, TT.TASK_TIME_NO, TT.TASK_TIME_DT, T.TASK_TYPE_CD, T.TASK_NM, T.TASK_PROJ_NM
        if tt[0] == None:
            ttid = PCT_DB.PCT_TimeDB.create_new_tasktime_row(
                self.DB_Handle, tid, tcd, dt, time)
        else:
            ttid = tt[0]
            PCT_DB.PCT_TimeDB.update_tasktime_time(self.DB_Handle, ttid, time)
        [lb2, lb4, lb5] = self.etllists[0]
        newtt = [ttid, tt[1], time, dt, tt[4], tt[5], tt[6], tt[7]]
        self.etllists[6][self.active_task_index] = newtt
        lb4.delete(self.active_task_index)
        lb5.delete(self.active_task_index)
        tm = str(int(time / 60))
        lb4.insert(self.active_task_index, "%s" % tm)
        lb5.insert(self.active_task_index, 'Yes')
        self.edit_task_quit()

    def delete_task(self):
        tt = self.etlists[4]
        ttid = tt[0]
        #    0              1              2              3                   4             5              6
        # TT.TASKTIME_ID, T.TASK_ID, TT.TASK_TIME_NO, TT.TASK_TIME_DT, T.TASK_TYPE_CD, T.TASK_NM, T.TASK_PROJ_NM
        PCT_DB.PCT_TimeDB.delete_tasktime_row(self.DB_Handle, ttid)
        [lb2, lb4, lb5] = self.etllists[0]
        tt = self.etllists[6][self.active_task_index]
        newtt = [None, tt[1], None, None, tt[4], tt[5], tt[6], tt[7]]
        self.etllists[6][self.active_task_index] = newtt
        lb4.delete(self.active_task_index)
        lb5.delete(self.active_task_index)
        lb4.insert(self.active_task_index, "None")
        lb5.insert(self.active_task_index, 'No')
        self.edit_task_quit()

    def add_field(self, r, labtext, twidth, ewidth, mode, default=None, valtype=None, tip=None):
        t = tk.Label(self.etlists[0], text=labtext, width=twidth, anchor='w')
        t.grid(row=r, column=0)
        atv = tk.StringVar()
        self.etlists[6].append(atv)
        if default != None:
            self.etlists[6][-1].set(default)
        self.etlists[9].append('key')
        self.etlists[7].append(self.etlists[0].register(self.val_task))
        self.etlists[8].append(self.etlists[0].register(self.val_error))
        if mode == 'D1':
            l = self.etlists[6][-1].get()
            at = tk.Label(self.etlists[0], width=ewidth, text=l)
            self.etlists[10].append([at])
            self.etlists[10][-1][0].grid(row=r, column=1, sticky=tk.W)
        elif mode == 'DA':
            dispnote = self.etlists[6][-1].get()
            at = tkst.ScrolledText(
                self.etlists[0], width=ewidth, height=5, wrap=tk.WORD)
            self.etlists[10].append(at)
            self.etlists[10][-1].grid(row=r, column=1)
            self.etlists[10][-1].insert(tk.INSERT, dispnote)
            self.etlists[10][-1].configure(state=tk.DISABLED)
        else:
            at = tk.Entry(self.etlists[0], width=ewidth, textvariable=self.etlists[6][-1],
                          validate=self.etlists[9][-1])
            vcmdix = len(self.etlists[7]) - 1
            at.config(validatecommand=(self.etlists[7][-1], '%V', '%P', '%W', vcmdix),
                      invalidcommand=(self.etlists[8][-1], '%V', '%P', '%W', vcmdix))
            self.etlists[10].append([at, valtype])
            self.etlists[10][-1][0].grid(row=r, column=1, sticky=tk.W)
        if tip != None:
            ToolTip.ToolTip(t, anchor='e', text=tip)

    def val_error(self, reason, value, widget, ix):
        i = int(ix)
        self.etlists[10][i][0].config(bg='red')
        self.etlists[10][i][0].focus_set()
        self.edtfldprocessbut.config(state=tk.DISABLED)

    def val_task(self, reason, value, widget, ix):
        i = int(ix)
        valtype = self.etlists[10][i][1]
        if reason == 'key':
            ok = self.valdict[valtype](value)
        self.etlists[0].after_idle(
            lambda v=reason: self.etlists[10][i][0].config(validate=v))
        if ok == True:
            self.etlists[10][i][0].config(bg='white')
            self.edtfldprocessbut.config(state=tk.ACTIVE)
        return ok

    def val_none(self, value):
        return True

    def val_a(self, value):
        if len(value) > 0:
            return True
        else:
            return False

    def val_sh(self, value):
        if value in ['S', 'H']:
            return True
        else:
            return False

    def val_nt(self, value):
        try:
            v = int(value)
            if v >= 0 and v <= 1440:
                return True
            else:
                return False
        except:
            return False

    def val_ns(self, value):
        try:
            v = int(value)
            if v >= 0 and v <= 999:
                return True
            else:
                return False
        except:
            return False

    def val_yn(self, value):
        if value in ['Y', 'N']:
            return True
        else:
            return False

    def val_yr(self, value):
        try:
            yr = date.today().strftime('%Y')
            yrp1 = str(int(yr) + 1)
            if value in [yr, yrp1]:
                return True
            else:
                return False
        except:
            return False

    def buildvaldict(self):
        self.valdict[None] = self.val_none
        self.valdict['A'] = self.val_a
        self.valdict['SH'] = self.val_sh
        self.valdict['NT'] = self.val_nt
        self.valdict['YN'] = self.val_yn
        self.valdict['NS'] = self.val_ns
        self.valdict['YR'] = self.val_yr
