import tkinter as tk
import PCT_PunchClock as punchclock
import PCT_DB as PCT_TimeDB
import helper_ToolTip as ToolTip
import helper_datepicker as datepicker
from datetime import date


class PCT_Tasks(tk.Frame):

    def __init__(self, master=None):
        self.master = master
        self.DB_Handle = None
        self.cb = []
        self.cbqb = None
        self.cbpb = None
        self.mqb = None
        self.mab = None
        self.msb = None
        self.mtb = None
        self.ftb = None
        self.cbintvar = []
        self.edtfld = []
        self.atqb = None
        self.atpb = None
        self.edtfldstringvar = []
        self.d_list = []
        self.h_list = []
        self.n_list = []
        self.holdpct = None
        self.holdctl = None
        self.holdmtl = None
        self.holdatl = None
        self.holddbh = None
        self.edtfldvalopt = []
        self.edtfldvcmd = []
        self.edtfldivcmd = []
        self.valdict = {}
        self.buildvaldict()
        self.holdmisctl = None
        self.miscqphoto = None
        self.miscqb = None
        self.miscpphoto = None
        self.pickfromtaskphoto = None
        self.miscpb = None
        self.valtoplvl = None
        self.valent = None
        self.misctiml = None
        self.misctime = None
        self.misctim = None
        self.adj_or_mov = None
        self.tid = None
        self.bix = None
        self.ftblist = []
        self.frombix = None
        self.fromtid = None
        self.activatemoveprocesssw = 0
        self.lbdict = {}

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

    def val_shi(self, value):
        if value in ['S', 'H', 'I']:
            return True
        else:
            return False

    def val_nt(self, value):
        try:
            v = int(value)
            if v >= 0 and v <= 480:
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
        self.valdict['SHI'] = self.val_shi
        self.valdict['NT'] = self.val_nt
        self.valdict['YN'] = self.val_yn
        self.valdict['NS'] = self.val_ns
        self.valdict['YR'] = self.val_yr

    def display_hidden(self, pct):
        self.holdpct = pct
        llists = punchclock.PCT_PunchClock.get_tasklists(self.holdpct)
        self.d_list = llists[0]
        self.h_list = llists[1]
        wlen = llists[2][0]
        self.holdctl = tk.Toplevel(pct)
        self.holdctl.title("Add Hidden Tasks to Active Display")
        self.holdctl.iconbitmap('digitalclock2.ico')
        self.quitphoto = tk.PhotoImage(file='log_off.gif')
        self.cbqb = tk.Button(self.holdctl, image=self.quitphoto,
                              command=lambda lltl=self.holdctl: punchclock.PCT_PunchClock.popupquit(pct, lltl))
        self.cbqb.grid(row=0, column=0)
        ToolTip.ToolTip(self.cbqb, anchor='e', text="Leave the window")
        if len(self.h_list) > 0:
            self.processphoto = tk.PhotoImage(file='process.gif')
            self.cbpb = tk.Button(
                self.holdctl, image=self.processphoto, command=self.process_display_hidden)
            self.cbpb.grid(row=0, column=1)
            ToolTip.ToolTip(
                self.cbpb, anchor='e', text="Process the selections")
        cbrow = 1
        self.cbintvar = []
        cbcol = 0
        cbcollim = len(self.h_list)
        cbrowlim = PCT_TimeDB.PCT_TimeDB.get_config_item(
            self.holddbh, 'SHOWHIDROWLIM')
        if cbrowlim == None:
            cbrowlim = 7
        cbcollim = int(cbcollim / int(cbrowlim))
        for ht in self.h_list:
            cbv = tk.IntVar()
            self.cbintvar.append(cbv)
            hn = ht[2] + '\n' + ht[3]
            cb = tk.Checkbutton(
                self.holdctl, text=hn, width=wlen, anchor='w', variable=self.cbintvar[-1])
            self.cb.append(cb)
            self.cb[-1].grid(row=cbrow, column=(cbcol * 2), columnspan=2)
            cbcol += 1
            if cbcol > cbcollim:
                cbrow += 1
                cbcol = 0

    def process_display_hidden(self):
        ix = -1
        change = 0
        poplist = []
        for cbi in self.cbintvar:
            ix += 1
            cb = cbi.get()
            if cb == 1:
                change += 1
                self.d_list.append(self.h_list[ix])
                poplist.append(ix)
        if change > 0:
            for pop in reversed(poplist):
                self.h_list.pop(pop)
            punchclock.PCT_PunchClock.set_tasklists(
                self.holdpct, [self.d_list, self.h_list, [change]])
        punchclock.PCT_PunchClock.popupquit(self.holdpct, self.holdctl)

    def init_add(self):
        self.edtfldstringvar = []
        self.edtfldvalopt = []
        self.edtfldvcmd = []
        self.edtfldivcmd = []
        self.edtfld = []
        self.edtfldprocessbut = None

    def add_new_task(self, pct, dbhandle):
        self.init_add()
        self.holdpct = pct
        self.dbhandle = punchclock.PCT_PunchClock.get_timeDB_handle(
            self.holdpct)
        llists = punchclock.PCT_PunchClock.get_tasklists(self.holdpct)
        self.d_list = llists[0]
        self.h_list = llists[1]
        self.holdatl = tk.Toplevel(pct)
        self.holdparent = self.holdatl
        self.holdatl.title("Add a New Task to the Active Display")
        self.holdatl.iconbitmap('digitalclock2.ico')
        self.quitphoto = tk.PhotoImage(file='log_off.gif')
        self.atqb = tk.Button(self.holdatl, image=self.quitphoto, anchor='w',
                              command=lambda lltl=self.holdatl: punchclock.PCT_PunchClock.popupquit(pct, lltl))
        self.atqb.grid(row=0, column=0)
        ToolTip.ToolTip(self.atqb, anchor='e', text="Leave the window")
        self.processphoto = tk.PhotoImage(file='process.gif')
        self.atpb = tk.Button(
            self.holdatl, image=self.processphoto, command=self.process_add_task)
        self.atpb.grid(row=0, column=1)
        self.edtfldprocessbut = self.atpb
        self.edtfldprocessbut.config(default=tk.DISABLED, state=tk.DISABLED)
        ToolTip.ToolTip(self.atpb, anchor='e', text="Add the task")
        # project, task, alert, show, autostart,guisort rptsort, taskyr is
        # current, get back taskid
        twidth = 25
        self.add_field(1, "Project Name", twidth, 50, None, None,
                       "The name of the project from PPM. This is optional")
        self.edtfld[0][0].focus_set()
        self.add_field(2, "Task Name", twidth, 50, None, 'A',
                       "The name of the task in the project. This is required")
        self.add_field(3, "(S)how or (H)ide", twidth, 2, 'S', 'SH',
                       "Initially show or hide this task. Hidden tasks can be added for the day, and will resume hidding on the next day")
        self.add_field(4, "Alarm Time (0,minutes)", twidth, 4, 0, 'NT',
                       "Should you have an alarm pop after n minutes to remind you about booking time to this task? Reminder so you can switch tasks appropriately")
        self.add_field(5, "Auto Start (only 1,Y/N)", twidth, 2, 'N', 'YN',
                       "Should this be the program to start accumulating time when the programs starts? Only one may have this value")
        self.add_field(6, "Screen Sort", twidth, 4, 999, 'NS',
                       "Sort order for shown tasks in the GUI list")
        self.add_field(7, "Report Sort`", twidth, 4, 999, 'NS',
                       "Sort order for the reports, should match the PPM time sheet order to may entry easier")
        yr = date.today().strftime('%Y')
        self.add_field(8, "Project Year", twidth, 5, yr, 'YR',
                       "The year for which this entry will be used. Current year or next year only.")

    def add_field(self, r, labtext, twidth, ewidth, default=None, valtype=None, tip=None):
        t = tk.Label(self.holdparent, text=labtext, width=twidth, anchor='w')
        t.grid(row=r, column=0)
        atv = tk.StringVar()
        self.edtfldstringvar.append(atv)
        if default != None:
            self.edtfldstringvar[-1].set(default)
        self.edtfldvalopt.append('focusout')
        self.edtfldvcmd.append(self.holdparent.register(self.val_task))
        self.edtfldivcmd.append(self.holdparent.register(self.val_error))
        at = tk.Entry(self.holdparent, width=ewidth, textvariable=self.edtfldstringvar[-1],
                      validate=self.edtfldvalopt[-1])
        vcmdix = len(self.edtfldvcmd) - 1
        at.config(validatecommand=(self.edtfldvcmd[-1], '%V', '%P', '%W', vcmdix),
                  invalidcommand=(self.edtfldivcmd[-1], '%V', '%P', '%W', vcmdix))
        self.edtfld.append([at, valtype])
        self.edtfld[-1][0].grid(row=r, column=1, sticky=tk.W)
        if tip != None:
            ToolTip.ToolTip(t, anchor='e', text=tip)

    def val_error(self, reason, value, widget, ix):
        i = int(ix)
        self.edtfld[i][0].config(bg='red')
        self.edtfld[i][0].focus_set()
        self.edtfldprocessbut.config(state=tk.DISABLED)

    def val_task(self, reason, value, widget, ix):
        i = int(ix)
        valtype = self.edtfld[i][1]
        if reason == 'focusout':
            ok = self.valdict[valtype](value)
        self.holdparent.after_idle(
            lambda v=reason: self.edtfld[i][0].config(validate=v))
        if ok == True:
            self.edtfld[i][0].config(bg='white')
            self.edtfldprocessbut.config(state=tk.ACTIVE)
        return ok

    def process_add_task(self):
        #    0  1   2  3  4   5    6   7
        #  pnm tnm sh at as gsrt rsrt yr
        #          SH    YN
        #    0    1     2    3    4    5     6     7     8     9
        # (tid, ttid, pnm, tnm, tat, tash, tast, tsrt, ttim, tdt) = self.tasklist[ix]
        elist = []
        for f in self.edtfld:
            v = f[0].get()
            elist.append(v)
        self.n_list = [
            None, None, None, None, None, None, None, None, None, None]
        self.n_list[2] = elist[0]
        self.n_list[3] = elist[1]
        print('b',elist,self.n_list)
        if elist[2].upper() == 'S':
            self.n_list[5] = 1
            elist[2] = 1
        elif elist[2].upper() == 'I':
            self.n_list[5] = 2
            elist[2] = 2
        else:
            self.n_list[5] = 0
            elist[2] = None
        print('a',elist,self.n_list)
        elist[3] = int(elist[3]) * 60
        self.n_list[4] = elist[3]
        if elist[3] == 0:
            elist[3] = None
        if elist[4].upper() == 'Y':
            self.n_list[6] = 1
            elist[4] = 1
        else:
            self.n_list[6] = 0
            elist[4] = None
        elist[5] = int(elist[5])
        elist[6] = int(elist[6])
        self.n_list[7] = elist[5]
        self.n_list[1] = -1
        self.n_list[8] = 0
        self.n_list[9] = date.today().strftime('%Y-%m-%d')
        new_tid = PCT_TimeDB.PCT_TimeDB.insert_task(self.dbhandle,
                                                    elist[1], elist[0], elist[3], elist[2], elist[4], elist[5], elist[6], elist[7])
        self.n_list[0] = new_tid
        self.d_list.append(self.n_list)
        punchclock.PCT_PunchClock.set_tasklists(
            self.holdpct, [self.d_list, self.h_list, [1]])
        punchclock.PCT_PunchClock.popupquit(self.holdpct, self.holdatl)

    # move time to here, from somwhere else (new popup)
    def movetasktime(self, pct, dbhandle, keys):
        self.activatemoveprocesssw = 0
        self.adj_or_mov = 'm'
        self.holdpct = pct
        llists = punchclock.PCT_PunchClock.get_tasklists(self.holdpct)
        self.d_list = llists[0]
        self.tid = keys[0]
        ttid = keys[1]
        self.bix = keys[2]
        self.holdpct = pct
        self.holddbh = dbhandle
        taskname = PCT_TimeDB.PCT_TimeDB.getTaskName(dbhandle, self.tid)
        self.holdmtl = tk.Toplevel(self.holdpct)
        self.valtoplvl = self.holdmtl
        self.holdmtl.title("Move Time to Task")
        self.holdmtl.iconbitmap('digitalclock2.ico')
        self.quitphoto = tk.PhotoImage(file='log_off.gif')
        self.mqb = tk.Button(self.holdmtl, image=self.quitphoto,
                             command=lambda lltl=self.holdmtl: punchclock.PCT_PunchClock.popupquit(pct, lltl))
        self.mqb.grid(row=0, column=0)
        ToolTip.ToolTip(self.mqb, anchor='e', text="Leave the window")
        self.pickfromtaskphoto = tk.PhotoImage(
            file='table-select-row-icon.gif')
        self.mtb = tk.Button(self.holdmtl, image=self.pickfromtaskphoto,
                             command=lambda: self.popup_from_task())
        self.mtb.grid(row=0, column=1)
        ToolTip.ToolTip(
            self.mtb, anchor='e', text="Pick task from which to take time")  # move
        self.processphoto = tk.PhotoImage(file='process.gif')
        self.mab = tk.Button(self.holdmtl, image=self.processphoto,
                             command=lambda: self.process_tofrom_timeadjustment())
        self.mab.grid(row=0, column=2)
        self.mab.config(state=tk.DISABLED)
        ToolTip.ToolTip(self.mab, anchor='e', text="Move the time")
        t = tk.Label(self.holdmtl, text=taskname[0], anchor='w', width=36)
        t.grid(row=1, column=0)
        self.modval = tk.StringVar()
        self.mvcmd = self.holdpct.register(self.val_time)
        self.mivcmd = self.holdpct.register(self.val_terror)
        self.edtfldivcmd.append(self.holdpct.register(self.val_terror))
        self.modtime = tk.Entry(self.holdmtl, width=5, textvariable=self.modval,
                                validate='key')
        self.valent = self.modtime
        self.modtime.config(validatecommand=(self.mvcmd, '%V', '%P', '%W'),
                            invalidcommand=(self.mivcmd, '%V', '%P', '%W'))
        self.modtime.grid(row=1, column=1, sticky=tk.W)
        self.modtime.focus_set()
        ToolTip.ToolTip(t, anchor='e',
                        text="Enter the number of minutes to move and press the process button after selecting the source task")

    def adjusttasktime(self, pct, dbhandle, keys):
        self.adj_or_mov = 'a'
        self.tid = keys[0]
        ttid = keys[1]
        self.bix = keys[2]
        self.holdpct = pct
        self.holddbh = dbhandle
        taskname = PCT_TimeDB.PCT_TimeDB.getTaskName(dbhandle, self.tid)
        self.holdmtl = tk.Toplevel(self.holdpct)
        self.valtoplvl = self.holdmtl
        self.holdmtl.title("Adjust Time for Task")
        self.holdmtl.iconbitmap('digitalclock2.ico')
        self.quitphoto = tk.PhotoImage(file='log_off.gif')
        self.mqb = tk.Button(self.holdmtl, image=self.quitphoto,
                             command=lambda lltl=self.holdmtl: punchclock.PCT_PunchClock.popupquit(pct, lltl))
        self.mqb.grid(row=0, column=0)
        ToolTip.ToolTip(self.mqb, anchor='e', text="Leave the window")
        self.plusphoto = tk.PhotoImage(file='Icojam-Blue-Bits-Math-add.gif')
        self.mab = tk.Button(self.holdmtl, image=self.plusphoto,
                             command=lambda lbix=self.bix: self.process_timeadjustment('A', lbix,'A'))
        self.mab.grid(row=0, column=1)
        self.mab.config(state=tk.DISABLED)
        ToolTip.ToolTip(self.mab, anchor='e', text="Add the time")
        self.minusphoto = tk.PhotoImage(file='Icojam-Blue-Bits-Math-minus.gif')
        self.msb = tk.Button(self.holdmtl, image=self.minusphoto,
                             command=lambda lbix=self.bix: self.process_timeadjustment('M', lbix,'A'))
        self.msb.grid(row=0, column=2)
        self.msb.config(state=tk.DISABLED)
        ToolTip.ToolTip(self.msb, anchor='e', text="Subtract the time")
        t = tk.Label(self.holdmtl, text=taskname[0], anchor='w', width=36)
        t.grid(row=1, column=0)
        self.modval = tk.StringVar()
        self.mvcmd = self.holdpct.register(self.val_time)
        self.mivcmd = self.holdpct.register(self.val_terror)
        self.edtfldivcmd.append(self.holdpct.register(self.val_terror))
        self.modtime = tk.Entry(self.holdmtl, width=5, textvariable=self.modval,
                                validate='key')
        self.valent = self.modtime
        self.modtime.config(validatecommand=(self.mvcmd, '%V', '%P', '%W'),
                            invalidcommand=(self.mivcmd, '%V', '%P', '%W'))
        self.modtime.grid(row=1, column=1, sticky=tk.W)
        self.modtime.focus_set()
        ToolTip.ToolTip(t, anchor='e',
                        text="Enter the number of minutes to change the time by and press the add or subtract button")

    def process_tofrom_timeadjustment(self):
        # print("process to from time adjust and ",__name__)
        # print(self.bix,self.frombix)
        self.process_timeadjustment('A', self.bix,'M')
        self.process_timeadjustment('M', self.frombix,'M')
        self.frombix = None
        self.activatemoveprocesssw = 0

    def process_timeadjustment(self, op, bix,adjustormove):
        min = self.modval.get()
        # print("process time adjustment")
        # print(op,bix,min)
        if len(min) > 0 and min != 0:
            sec = int(min) * 60
            if op == 'M':
                sec *= -1
            punchclock.PCT_PunchClock.adjust_task_time(self.holdpct, bix, sec)
            if adjustormove == 'A':
                self.holddbh.timeadjustok_false()
        punchclock.PCT_PunchClock.popupquit(self.holdpct, self.holdmtl)

    def val_time(self, reason, value, widget):
        ok = True
        if len(value) > 0:
            ok = False
            ok = value.isnumeric()
            if ok:
                if int(value) > int(PCT_TimeDB.PCT_TimeDB.get_config_item(self.holddbh, "DAYLEN")) / 60:
                    ok = False
            self.valtoplvl.after_idle(
                lambda r=reason: self.valent.config(validate=r))
            if ok == True:
                self.valent.config(bg='white')
                try:
                    self.edtfldprocessbut.config(state=tk.ACTIVE)
                except:
                    if self.adj_or_mov == 'm':
                        self.activatemoveprocesssw += 1
                        self.activatemoveprocess()
                    if self.adj_or_mov == 'a':
                        self.mab.config(state=tk.ACTIVE)
                        self.msb.config(state=tk.ACTIVE)
        return ok

    def activatemoveprocess(self):
        if self.activatemoveprocesssw > 1:
            self.mab.config(state=tk.ACTIVE)

    def button_pop_from_task(self, brow):
        self.activatemoveprocesssw += 1
        self.activatemoveprocess()
        self.frombix = self.ftblist[brow][1]
        # print("button pop from task")
        # print("row ",brow,self.frombix)
        task = self.d_list[self.frombix]
        taskname = task[2] + '\n' + task[3]
        t = tk.Label(self.holdmtl, text=taskname, anchor='w', width=36)
        t.grid(row=2, column=0)
        self.ftblist.append(t)
        punchclock.PCT_PunchClock.popupquit(self.holdmtl, self.holdftl)

    def popup_from_task(self):
        self.holdftl = tk.Toplevel(self.holdmtl)
        self.holdftl.title("Move Time From Task")
        self.holdftl.iconbitmap('digitalclock2.ico')
        self.ftb = tk.Button(self.holdftl, image=self.quitphoto,
                             command=lambda lltl=self.holdftl, lpct=self.holdpct: punchclock.PCT_PunchClock.popupquit(lpct, lltl))
        gridrow = 0
        self.ftblist = []
        self.ftb.grid(row=gridrow, column=0)
        ToolTip.ToolTip(self.ftb, anchor='e', text="Leave the window")
        max_width = 36
        for t in self.d_list:
            n = t[2] + '\n' + t[3]
            if len(n) > max_width:
                max_width = len(n)
        # print("popup from task")
        # print("bix",self.bix)
        for ix, t in enumerate(self.d_list):
            # print("dlist ", ix, t)
            if ix != self.bix:
                gridrow += 1
                n = t[2] + '\n' + t[3]
                nb = tk.Button(self.holdftl, text=n, width=max_width, anchor='w', bg='white',
                               command=lambda lr=gridrow - 1, lt=t[0]: self.button_pop_from_task(lr))
                nb.grid(row=gridrow, column=0)
                ToolTip.ToolTip(nb, anchor='e', text="Source of time to move")
                nbix = (nb, ix)
                self.ftblist.append(nbix)

    def val_terror(self, reason, value, widget):
        self.valent.config(bg='red')
        try:
            self.edtfldprocessbut.config(state=tk.DISABLED)
        except:
            self.mab.config(state=tk.DISABLED)
            if self.adj_or_mov == 'a':
                self.msb.config(state=tk.DISABLED)
        self.valent.focus_set()

    def datepicker_pop(self):
        self.datepicker_tl = tk.Toplevel(self.master)
        self.datepicker_tl.iconbitmap('digitalclock2.ico')
        ldate = datepicker.Calendar(self.datepicker_tl, self.datedhandle)
        self.edtfldprocessbut.config(state=tk.ACTIVE)

    def misc_tasks_display(self, pcthandle, dbhandle):  # date field
        self.holdpct = pcthandle
        self.holddbh = dbhandle
        self.misctim = None
        self.holdmisctl = tk.Toplevel(pcthandle)
        self.holdmisctl.title("Add Time to a Misc. Task")
        self.holdmisctl.iconbitmap('digitalclock2.ico')
        self.miscqphoto = tk.PhotoImage(file='log_off.gif')
        self.miscqb = tk.Button(self.holdmisctl, image=self.miscqphoto,
                                command=lambda lltl=self.holdmisctl: punchclock.PCT_PunchClock.popupquit(pcthandle, lltl))
        self.miscqb.grid(row=0, column=0)
        ToolTip.ToolTip(self.miscqb, anchor='e', text="Leave the window")
        self.miscpphoto = tk.PhotoImage(file='process.gif')
        self.miscpb = tk.Button(self.holdmisctl, image=self.miscpphoto,
                                command=self.process_misc_task)
        self.miscpb.grid(row=0, column=1)
        self.edtfldprocessbut = self.miscpb
        self.edtfldprocessbut.config(default=tk.DISABLED, state=tk.DISABLED)
        ToolTip.ToolTip(self.miscpb, anchor='w', text="Add the time")
        self.tlen = PCT_TimeDB.PCT_TimeDB.get_max_misctask_len(dbhandle)
        self.tlist = PCT_TimeDB.PCT_TimeDB.get_misctask_nm(dbhandle)

        r = 0
        self.rbbt = []
        self.rbtcv = tk.IntVar()
        v = -1
        for taskl in self.tlist:
            task = [taskl[0]]
            r += 1
            v += 1
            self.rbbt.append(tk.Radiobutton(self.holdmisctl, indicatoron=0, text=task[0],
                                            value=v, variable=self.rbtcv,
                                            borderwidth=2, width=self.tlen, state=tk.NORMAL, offrelief=tk.RAISED, relief=tk.FLAT))
            self.rbbt[len(self.rbbt) - 1].grid(row=r, column=0)

        self.misccalphoto = tk.PhotoImage(file='Google-Calendar-icon.gif')
        self.misccalb = tk.Button(self.holdmisctl, image=self.misccalphoto,
                                  command=self.datepicker_pop)
        self.misccalb.grid(row=1, column=1)
        ToolTip.ToolTip(
            self.misccalb, anchor='e', text="Use a Calendar Widget to select the date")

        self.datedhandle = datepicker.DateData()
        self.dt = self.datedhandle.getDateDatadisp()
        dl = tk.Label(self.holdmisctl, text="Date", anchor='e', width=10)
        dl.grid(row=2, column=1)
        dl = tk.Label(
            self.holdmisctl, textvariable=self.dt, width=23, anchor='w')
        dl.grid(row=2, column=2)

        r = 3
        self.rbbd = []
        self.rbdcv = tk.IntVar()
        daytype = ["Full Day", "Half Day", "Time in minutes"]
        v = -1
        for day in daytype:
            r += 1
            v += 1
            self.rbbd.append(tk.Radiobutton(self.holdmisctl, indicatoron=0, text=day,
                                            value=v, variable=self.rbdcv,
                                            command=lambda ltl=self.holdmisctl, lrbv=self.rbdcv: self.process_misc_dayt(
                                                ltl, lrbv),
                                            borderwidth=2, width=self.tlen, state=tk.NORMAL, offrelief=tk.RAISED, relief=tk.FLAT))
            self.rbbd[len(self.rbbd) - 1].grid(row=r + 1, column=2)

    def process_misc_dayt(self, tl, rbv):
        dayix = rbv.get()
        if dayix == 2:
            self.misctiml = tk.Label(
                self.holdmisctl, text="Minutes", anchor='e', width=10)
            self.misctiml.grid(row=8, column=1)
            self.misctim = tk.StringVar()
            self.misctime = tk.Entry(
                self.holdmisctl, width=6, textvariable=self.misctim, validate='key')
            self.misctime.grid(row=8, column=2)
            self.misctimevcmd = self.holdpct.register(self.val_time)
            self.misctimeivcmd = self.holdpct.register(self.val_terror)
            self.valtoplvl = self.holdmisctl
            self.valent = self.misctime
            self.misctime.config(validatecommand=(self.misctimevcmd, '%V', '%P', '%W'),
                                 invalidcommand=(self.misctimeivcmd, '%V', '%P', '%W'))
            self.misctime.focus_set()
            ToolTip.ToolTip(
                self.misctiml, anchor='e', text="Enter the time in minutes, not more than a working day's time.")
            ToolTip.ToolTip(
                self.misctime, anchor='e', text="Enter the time in minutes, not more than a working day's time.")
        else:
            if self.misctiml != None:
                self.misctiml.destroy()
                self.misctiml = None
            if self.misctime != None:
                self.misctime.destroy()
                self.misctime = None
                self.misctim = None

    def process_misc_task(self):
        taskix = self.rbtcv.get()
        dayix = self.rbdcv.get()
        dt = self.dt.get()
        if self.misctim != None:
            timnostr = self.misctim.get()
            timno = int(timnostr) * 60
        else:
            timno = int(
                PCT_TimeDB.PCT_TimeDB.get_config_item(self.holddbh, "DAYLEN"))
            if dayix == 1:
                timno /= 2
        tid = self.tlist[taskix][1]
        PCT_TimeDB.PCT_TimeDB.insert_misc_task_time(
            self.holddbh, tid, timno, dt[0:10])
        punchclock.PCT_PunchClock.popupquit(self.holdpct, self.holdmisctl)

    def lb_get_sel(self, event):
        self.lbdict[event.widget][0] = event.widget.curselection()[0]

    def lb_move_up(self, lb):
        """ Moves the item at position pos up by one """
        pos = self.lbdict[lb][0]
        h = self.lbdict[lb][6]
        if pos != 0:
            text = lb.get(pos)
            lb.delete(pos)
            lb.insert(pos - 1, text)
            lb.selection_set(pos - 1)
            self.lbdict[lb][0] = pos - 1
            # if pos >= h:
            lb.yview_scroll(-1, 'units')
            lb.see(pos)

    def lb_move_down(self, lb):
        """ Moves the item at position pos down by one """
        pos = self.lbdict[lb][0]
        h = self.lbdict[lb][6]
        len = self.lbdict[lb][7]
        if pos <= len:
            text = lb.get(pos)
            lb.delete(pos)
            lb.insert(pos + 1, text)
            lb.selection_set(pos + 1)
            self.lbdict[lb][0] = pos + 1
            # if pos >= h:
            lb.yview_scroll(1, 'units')
            lb.see(pos)

    def lb_order_tasks(self, pcthandle, dbhandle, opt):
        self.DB_Handle = dbhandle
        holdlbtl = tk.Toplevel(pcthandle)
        holdlbtl.title("Order Tasks")
        holdlbtl.iconbitmap('digitalclock2.ico')
        lbqphoto = tk.PhotoImage(file='log_off.gif')
        lbqb = tk.Button(holdlbtl, image=lbqphoto,
                         command=lambda lltl=holdlbtl: punchclock.PCT_PunchClock.popupquit(pcthandle, lltl))
        lbqb.grid(row=0, column=0)
        ToolTip.ToolTip(lbqb, anchor='e', text="Leave the window")
        lbpphoto = tk.PhotoImage(file='process.gif')
        lbpb = tk.Button(holdlbtl, image=lbpphoto)
        lbpb.grid(row=0, column=1)
        ToolTip.ToolTip(lbpb, anchor='w', text="Apply the new Order")
        tasks = self.DB_Handle.getallTasksrpt(opt)
        w = 0
        for task in tasks:
            if w < len(task[0]):
                w = len(task[0])
        h = (len(tasks) + 2) if len(tasks) < 18 else 20
        lb = tk.Listbox(holdlbtl, width=w, height=h)
        lb.grid(row=1, column=0)
        lbpb.config(
            command=lambda relatedlb=lb: self.process_apply_new_order(relatedlb))
        ToolTip.ToolTip(
            lb, anchor='w', text="Select an item with the mouse and use the arrows to change the order")
        yscroll = tk.Scrollbar(holdlbtl, command=lb.yview, orient=tk.VERTICAL)
        yscroll.grid(row=1, column=1, sticky=tk.N + tk.S)
        lb.configure(yscrollcommand=yscroll.set)
        lbuphoto = tk.PhotoImage(file='arrow-up-icon.gif')
        buttonup = tk.Button(
            holdlbtl, image=lbuphoto, command=lambda lb=lb: self.lb_move_up(lb))
        buttonup.grid(row=1, column=2, sticky=tk.E + tk.S)
        ToolTip.ToolTip(buttonup, anchor='w', text="Move the selection up")
        lbdphoto = tk.PhotoImage(file='arrow-down-icon.gif')
        buttondn = tk.Button(
            holdlbtl, image=lbdphoto, command=lambda lb=lb: self.lb_move_down(lb))
        buttondn.grid(row=1, column=2, sticky=tk.E + tk.N)
        ToolTip.ToolTip(buttonup, anchor='w', text="Move the selection down")
        dictlist = {}
        buttons = [lbqphoto, lbpphoto, lbuphoto, lbdphoto,
                   lbqb, lbpb, buttonup, buttondn, yscroll]
        for task in tasks:
            lb.insert(tk.END, task[0])
            dictlist[task[0]] = task[1]
        self.lbdict[lb] = [
            None, opt, pcthandle, holdlbtl, dictlist, buttons, h, len(tasks)]
        lb.bind('<ButtonRelease-1>', self.lb_get_sel)

    def process_apply_new_order(self, relatedlb):
        opt = self.lbdict[relatedlb][1]
        ptl = self.lbdict[relatedlb][2]
        tl = self.lbdict[relatedlb][3]
        dictlist = self.lbdict[relatedlb][4]
        lblist = relatedlb.get(0, tk.END)
        newsortno = 0
        for lbl in lblist:
            newsortno += 10
            self.DB_Handle.update_task_sort(opt, dictlist.get(lbl), newsortno)
        punchclock.PCT_PunchClock.popupquit(ptl, tl)

    def edit_tasks_list(self, pcthandle, dbhandle):
        self.etllists = [
            None, None, None, None, None, None, None, pcthandle, dbhandle]
        # 0 is list of listboxes
        # 1 is common vscroll
        # 2 is toplevel
        # 3 is button image
        # 4 is button
        # 5 is list of labels
        # 6 is the list of task_id values for the tasks
        # 7 is pcthandle
        # 8 is dbhandle
        self.DB_Handle = dbhandle
        holdetltl = tk.Toplevel(pcthandle)
        holdetltl.title("Edit Tasks")
        holdetltl.iconbitmap('digitalclock2.ico')
        self.etllists[2] = holdetltl
        etlqphoto = tk.PhotoImage(file='log_off.gif')
        self.etllists[3] = [etlqphoto]
        etlqb = tk.Button(holdetltl, image=etlqphoto,
                          command=lambda lltl=holdetltl: punchclock.PCT_PunchClock.popupquit(pcthandle, lltl))
        self.etllists[4] = [etlqb]
        etlqb.grid(row=0, column=0)
        ToolTip.ToolTip(etlqb, anchor='e', text="Leave the window")
        etlcnyphoto = tk.PhotoImage(file='fire-ball-icon32-hi.gif')
        self.etllists[3].append(etlcnyphoto)
        etlcnyb = tk.Button(holdetltl, image=etlcnyphoto,
                            command=lambda: PCT_TimeDB.PCT_TimeDB.copytasksforwardoneyear(dbhandle))
        self.etllists[4].append(etlcnyb)
        etlcnyb.grid(row=0, column=1)
        ToolTip.ToolTip(etlcnyb, anchor='e', text="Copy Year Forward")
        tasks = self.DB_Handle.getallTasks()
        tnwidth = self.DB_Handle.get_max_but_len() * 2
        vsb = tk.Scrollbar(
            holdetltl, orient="vertical", command=self.etl_OnVsb)
        self.etllists[1] = vsb
        cl2 = tk.Label(holdetltl, text='Project Task')
        cl4 = tk.Label(holdetltl, text='Alarm Time')
        cl5 = tk.Label(holdetltl, text='Show/Hide/Invisible')
        cl6 = tk.Label(holdetltl, text='AutoStart')
        cl2.grid(row=1, column=0)
        cl4.grid(row=1, column=1)
        cl5.grid(row=1, column=2)
        cl6.grid(row=1, column=3)
        lb2 = tk.Listbox(holdetltl, yscrollcommand=vsb.set,
                         exportselection=1, width=tnwidth, selectmode=tk.SINGLE)
        ToolTip.ToolTip(
            lb2, anchor='e', text="Select the task to edit by clicking on the name")
        lb4 = tk.Listbox(holdetltl, yscrollcommand=vsb.set,
                         exportselection=0, takefocus=0, relief=tk.FLAT)
        lb5 = tk.Listbox(holdetltl, yscrollcommand=vsb.set,
                         exportselection=0, takefocus=0, relief=tk.FLAT)
        lb6 = tk.Listbox(holdetltl, yscrollcommand=vsb.set,
                         exportselection=0, takefocus=0, relief=tk.FLAT)
        vsb.grid(row=2, column=4, sticky=tk.N + tk.S)
        lb2.grid(row=2, column=0)
        lb4.grid(row=2, column=1)
        lb5.grid(row=2, column=2)
        lb6.grid(row=2, column=3)
        lb2.bind("<MouseWheel>", self.etl_OnMouseWheel)
        lb2.bind('<ButtonRelease-1>', self.etl_process_sel)
        lb4.bind("<MouseWheel>", self.etl_OnMouseWheel)
        lb5.bind("<MouseWheel>", self.etl_OnMouseWheel)
        lb6.bind("<MouseWheel>", self.etl_OnMouseWheel)
        tidlist = []
        #    0    1     2    3    4    5     6     7     8     9
        # (tid, ttid, pnm, tnm, tat, tash, tast, tsrt, ttim, tdt) = self.tasklist[ix]
        for task in tasks:
            nm = task[2] + ' ' + task[3]
            lb2.insert("end", "%s" % nm)
            at = int(int(task[4]) / 60)
            at = str(at) if at > 0 else 'None'
            lb4.insert("end", "%s" % at)
            sh = 'Show' if task[5] == 1 else 'Hide'
            shi = ['Hide','Show','Invisible']
            sh = shi[task[5]]
            lb5.insert("end", "%s" % sh)
            ast = 'Yes' if task[5] == 1 else 'No'
            lb6.insert("end", "%s" % ast)
            tidlist.append(task[0])
        self.etllists[0] = [lb2, lb4, lb5, lb6]
        self.etllists[5] = [cl2, cl4, cl5, cl6]
        self.etllists[6] = tidlist

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
        tid = self.etllists[6][ix]
        tl = self.etllists[2]
        tl.destroy()
        self.edit_task(self.etllists[7], self.etllists[8], tid)

    def edit_task(self, pcthandle, dbhandle, tid):
        self.init_add()
        self.etlists = [None, None, None, None, None, None, 'N']
        self.DB_Handle = dbhandle
        self.holdpct = pcthandle
        holdettl = tk.Toplevel(pcthandle)
        holdettl.title("Edit Task")
        holdettl.iconbitmap('digitalclock2.ico')
        self.etlists[0] = [holdettl, pcthandle, dbhandle]
        # 0 is [toplevel,pcthandle,dbhandle]
        # 1 is button image
        # 2 is button
        # 3 is button image
        # 4 is button
        # 5 is list of attributes [tid,pnm,tnm,at,ast,swhd]
        # 6 is change all projects
        quitphoto = tk.PhotoImage(file='log_off.gif')
        self.etlists[1] = quitphoto
        etqb = tk.Button(
            holdettl, image=quitphoto, anchor='w', command=self.edit_task_quit)
        etqb.grid(row=0, column=0)
        self.etlists[2] = etqb
        ToolTip.ToolTip(etqb, anchor='e', text="Leave the window")
        processphoto = tk.PhotoImage(file='process.gif')
        self.etlists[3] = processphoto
        self.edtfldprocessbut = tk.Button(
            holdettl, image=processphoto, anchor='e', command=self.edit_task_update)
        self.edtfldprocessbut.grid(row=0, column=1)
        self.edtfldprocessbut.config(default=tk.DISABLED, state=tk.DISABLED)
        self.etlists[4] = self.edtfldprocessbut
        ToolTip.ToolTip(
            self.edtfldprocessbut, anchor='e', text="Process the changes")
        task = self.etlists[0][2].getTask(tid)
        (tid, pnm, tnm, at, ast, swhd) = task
        at = str(int(int(at) / 60))
        if at == 0:
            at = None
        ast = 'N' if ast == 0 else 'Y'
        # swhd = 'H' if swhd == 0 else 'S'
        shi = ['H','S','I']
        swhd = shi[swhd]
        self.etlists[5] = [tid, pnm, tnm, at, ast, swhd]
        self.edtfldvalopt = []
        self.holdparent = self.etlists[0][0]
        twidth = 25
        self.add_field(1, "Project Name", twidth, 50, pnm, 'A',
                       "The name of the project from PPM. This is optional")
        self.edtfld[0][0].focus_set()
        self.add_field(2, "Update all tasks with new name", twidth, 2, 'N', 'YN',
                       "Reset the project name for all of the tasks with this project")
        self.add_field(3, "Task Name", twidth, 50, tnm, 'A',
                       "The name of the task in the project. This is required")
        self.add_field(4, "(S)how or (H)ide or (I)nvisible", twidth, 2, swhd, 'SHI',
                       "Initially show or hide this task. Hidden tasks can be added for the day, and will resume hidding on the next day. Invisable tasks are not in use, will not be copied forward to next year")
        self.add_field(5, "Alarm Time (0,minutes)", twidth, 4, at, 'NT',
                       "Should you have an alarm pop after n minutes to remind you about booking time to this task? Reminder so you can switch tasks appropriately")
        self.add_field(6, "Auto Start (only 1,Y/N)", twidth, 2, ast, 'YN',
                       "Should this be the program to start accumulating time when the programs starts? Only one may have this value")

    def edit_task_quit(self):
        self.etlists[0][0].destroy()
        self.edit_tasks_list(self.etlists[0][1], self.etlists[0][2])

    def edit_task_update(self):
        pnm = self.edtfld[0][0].get()
        allpnm = self.edtfld[1][0].get()
        tnm = self.edtfld[2][0].get()
        tsh = self.edtfld[3][0].get()
        tat = self.edtfld[4][0].get()
        tas = self.edtfld[5][0].get()
        tid = self.etlists[5][0]
        self.etlists[0][2].setTask([tid, pnm, tnm, tat, tsh, tas])
        self.holdpct.update_task_name(tid, pnm, tnm)
        punchclock.PCT_PunchClock.reset_alarmcycletime(self.holdpct, tid, tat)
        if allpnm == 'Y':
            self.etlists[0][2].setTaskProj(self.etlists[5][1], pnm)
        self.etlists[0][0].destroy()
        self.edit_tasks_list(self.etlists[0][1], self.etlists[0][2])

    def edit_config_list(self, pcthandle, dbhandle):
        self.confglists = [
            None, None, None, None, None, None, None, pcthandle, dbhandle, None, None]
        # 0 is list of listboxes
        # 1 is common vscroll
        # 2 is toplevel
        # 3 is button image
        # 4 is button
        # 5 is list of labels
        # 6 is config key list
        # 7 is pcthandle
        # 8 is dbhandle
        # 9 is button image for add_field
        # 10 is button for add
        self.DB_Handle = dbhandle
        holdconfgltl = tk.Toplevel(pcthandle)
        holdconfgltl.title("Edit Configuration")
        holdconfgltl.iconbitmap('digitalclock2.ico')
        self.confglists[2] = holdconfgltl
        confglqphoto = tk.PhotoImage(file='log_off.gif')
        self.confglists[3] = confglqphoto
        confglqb = tk.Button(holdconfgltl, image=confglqphoto, anchor='w',
                             command=lambda lltl=holdconfgltl: punchclock.PCT_PunchClock.popupquit(pcthandle, lltl))
        self.confglists[4] = confglqb
        confglqb.grid(row=0, column=0)
        ToolTip.ToolTip(confglqb, anchor='e', text="Leave the window")

        confglaphoto = tk.PhotoImage(file='Icojam-Blue-Bits-Math-add.gif')
        self.confglists[9] = confglaphoto
        confglab = tk.Button(holdconfgltl, image=confglaphoto, anchor='e',
                             command=lambda: self.add_config(pcthandle, dbhandle))
        self.confglists[10] = confglab
        confglab.grid(row=0, column=1)
        ToolTip.ToolTip(
            confglab, anchor='e', text="Add a new configuration key value pair")

        configs = self.DB_Handle.get_config()
        vsb = tk.Scrollbar(
            holdconfgltl, orient="vertical", command=self.confgl_OnVsb)
        self.confglists[1] = vsb
        cl0 = tk.Label(holdconfgltl, text='Config')
        cl1 = tk.Label(holdconfgltl, text='Value')
        cl2 = tk.Label(holdconfgltl, text='Description')
        cl0.grid(row=1, column=0)
        cl1.grid(row=1, column=1)
        cl2.grid(row=1, column=2)
        lb0 = tk.Listbox(holdconfgltl, yscrollcommand=vsb.set,
                         exportselection=1, width=25, selectmode=tk.SINGLE)
        ToolTip.ToolTip(
            lb0, anchor='e', text="Select the item to edit by clicking on the name")
        lb1 = tk.Listbox(holdconfgltl, yscrollcommand=vsb.set,
                         exportselection=0, width=15, takefocus=0, relief=tk.FLAT)
        lb2 = tk.Listbox(holdconfgltl, yscrollcommand=vsb.set,
                         exportselection=0, width=50, takefocus=0, relief=tk.FLAT)
        vsb.grid(row=2, column=3, sticky=tk.N + tk.S)
        lb0.grid(row=2, column=0)
        lb1.grid(row=2, column=1)
        lb2.grid(row=2, column=2)
        lb0.bind("<MouseWheel>", self.confgl_OnMouseWheel)
        lb0.bind('<ButtonRelease-1>', self.confgl_process_sel)
        lb1.bind("<MouseWheel>", self.confgl_OnMouseWheel)
        lb2.bind("<MouseWheel>", self.confgl_OnMouseWheel)
        cflist = []
        for conf in configs:
            lb0.insert("end", "%s" % conf[0])
            lb1.insert("end", "%s" % conf[1])
            lb2.insert("end", "%s" % conf[2])
            cflist.append(conf[0])
        self.confglists[0] = [lb0, lb1, lb2]
        self.confglists[5] = [cl0, cl1, cl2]
        self.confglists[6] = cflist

    def confgl_OnVsb(self, *args):
        for confgl in self.confglists[0]:
            confgl.yview(*args)

    def confgl_OnMouseWheel(self, event):
        for confgl in self.confglists[0]:
            confgl.yview("scroll", event.delta, "units")
        # this prevents default bindings from firing, which
        # would end up scrolling the widget twice
        return "break"

    def confgl_process_sel(self, event):
        ix = event.widget.curselection()[0]
        tl = self.confglists[2]
        key = self.confglists[6][ix]
        tl.destroy()
        self.edit_config(self.confglists[7], self.confglists[8], key)

    def edit_config(self, pcthandle, dbhandle, key):
        self.init_add()
        self.confglists = [None, None, None, None, None, None, 'N']
        self.DB_Handle = dbhandle
        holdconfgtl = tk.Toplevel(pcthandle)
        holdconfgtl.title("Edit Config Item")
        holdconfgtl.iconbitmap('digitalclock2.ico')
        self.confglists[0] = [holdconfgtl, pcthandle, dbhandle]
        # 0 is [toplevel,pcthandle,dbhandle]
        # 1 is button image
        # 2 is button
        # 3 is button image
        # 4 is button
        # 5 is list of attributes
        # 6 is change all projects
        quitphoto = tk.PhotoImage(file='log_off.gif')
        self.confglists[1] = quitphoto
        etqb = tk.Button(
            holdconfgtl, image=quitphoto, anchor='w', command=self.edit_config_quit)
        etqb.grid(row=0, column=0)
        self.confglists[2] = etqb
        ToolTip.ToolTip(etqb, anchor='e', text="Leave the window")
        processphoto = tk.PhotoImage(file='process.gif')
        self.confglists[3] = processphoto
        self.edtfldprocessbut = tk.Button(
            holdconfgtl, image=processphoto, anchor='e', command=self.edit_config_update)
        self.edtfldprocessbut.grid(row=0, column=1)
        self.edtfldprocessbut.config(default=tk.DISABLED, state=tk.DISABLED)
        self.confglists[4] = self.edtfldprocessbut
        ToolTip.ToolTip(
            self.edtfldprocessbut, anchor='e', text="Process the changes")
        confgitem = self.confglists[0][2].get_config(key)
        self.confglists[5] = confgitem
        self.edtfldvalopt = []
        self.holdparent = self.confglists[0][0]
        twidth = 25
        self.add_field(1, "Config", twidth, 25, self.confglists[5][0][0], 'A',
                       "The config item key")
        self.edtfld[0][0].focus_set()
        self.add_field(2, "Value", twidth, 50, self.confglists[5][0][1], 'A',
                       "Value for config item")
        self.add_field(3, "Description", twidth, 50, self.confglists[5][0][2], None,
                       "Description of the config item")

    def edit_config_quit(self):
        self.confglists[0][0].destroy()
        self.edit_config_list(self.confglists[0][1], self.confglists[0][2])

    def edit_config_update(self):
        key = self.edtfld[0][0].get()
        val = self.edtfld[1][0].get()
        desc = self.edtfld[2][0].get()
        self.confglists[0][2].set_config_item(key, val, desc)
        self.confglists[0][0].destroy()
        self.edit_config_list(self.confglists[0][1], self.confglists[0][2])

    def add_config_insert(self):
        key = self.edtfld[0][0].get()
        val = self.edtfld[1][0].get()
        desc = self.edtfld[2][0].get()
        self.confglists[0][2].add_config_item(key, val, desc)
        self.confglists[0][0].destroy()
        self.edit_config_list(self.confglists[0][1], self.confglists[0][2])

    def add_config(self, pcthandle, dbhandle):
        self.init_add()
        self.confglists[2].destroy()
        self.confglists = [None, None, None, None, None, None, 'N']
        self.DB_Handle = dbhandle
        holdconfgtl = tk.Toplevel(pcthandle)
        holdconfgtl.title("Edit Config Item")
        self.confglists[2] = holdconfgtl
        self.confglists[0] = [holdconfgtl, pcthandle, dbhandle]
        # 0 is [toplevel,topl,dbhandle]
        # 1 is button image
        # 2 is button
        # 3 is button image
        # 4 is button
        # 5 is list of attributes
        # 6 is change all projects
        quitphoto = tk.PhotoImage(file='log_off.gif')
        self.confglists[1] = quitphoto
        etqb = tk.Button(
            holdconfgtl, image=quitphoto, anchor='w', command=self.edit_config_quit)
        etqb.grid(row=0, column=0)
        self.confglists[2] = etqb
        ToolTip.ToolTip(etqb, anchor='e', text="Leave the window")
        processphoto = tk.PhotoImage(file='process.gif')
        self.confglists[3] = processphoto
        self.edtfldprocessbut = tk.Button(
            holdconfgtl, image=processphoto, anchor='e', command=self.add_config_insert)
        self.edtfldprocessbut.grid(row=0, column=1)
        self.edtfldprocessbut.config(default=tk.DISABLED, state=tk.DISABLED)
        self.confglists[4] = self.edtfldprocessbut
        ToolTip.ToolTip(
            self.edtfldprocessbut, anchor='e', text="Process the addition")
        self.edtfldvalopt = []
        self.holdparent = self.confglists[0][0]
        twidth = 25
        self.add_field(1, "Config", twidth, 25, None, 'A',
                       "The config item key")
        self.edtfld[0][0].focus_set()
        self.add_field(2, "Value", twidth, 50, None, 'A',
                       "Value for config item")
        self.add_field(3, "Description", twidth, 50, None, None,
                       "Description of the config item")

    def dummylastline(self):
        pass
