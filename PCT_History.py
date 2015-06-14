import tkinter as tk
import PCT_PunchClock as punchclock
import PCT_DB as PCT_TimeDB
import helper_ToolTip as ToolTip
import helper_datepicker as datepicker
from datetime import datetime, date, timedelta
import math
import os
import logging
import textwrap
# import operator

class PCT_History(tk.Frame):
    def __init__(self, master=None):
        self.master = master
        self.DB_Handle = None
        self.history_tl = None
        self.quitphoto = None
        self.pct = None
        self.datedhandle = None
        self.dt = None
        self.listshowed = False
        self.tasklistrows = []
        self.lstb = None
        self.prcb = None
    def historical_edit(self,pct,dbh):
        self.pct = pct
        self.DB_Handle = dbh
        self.history_tl = tk.Toplevel(self.pct)
        self.history_tl.iconbitmap('digitalclock2.ico')
        self.history_tl.title("Edit a specific date's time'")
        self.qphoto=tk.PhotoImage(file='log_off.gif')
        self.qb = tk.Button(self.history_tl, image=self.qphoto,
                command=lambda lltl = self.history_tl \
                :punchclock.PCT_PunchClock.popupquit(self.pct,lltl))
        self.qb.grid(row=0, column=0)
        ToolTip.ToolTip(self.qb, anchor='e', text="Leave the window")
        self.calphoto=tk.PhotoImage(file='Google-Calendar-icon.gif')
        self.calb = tk.Button(self.history_tl, image=self.calphoto,
                command=self.datepicker_pop)
        self.calb.grid(row=0, column=1)
        ToolTip.ToolTip(self.calb, anchor='e', text="Use a Calendar Widget to select the date")        
        self.lstphoto=tk.PhotoImage(file='list.gif')
        self.lstb = tk.Button(self.history_tl, image=self.lstphoto, state = tk.DISABLED,
                command=lambda:self.show_a_dates_tasks())
        self.lstb.grid(row=0, column=2)
        ToolTip.ToolTip(self.lstb, anchor='e', text="Show the tasks for the date")
        self.prcphoto=tk.PhotoImage(file='process.gif')
        self.prcb = tk.Button(self.history_tl, image=self.prcphoto, state = tk.DISABLED,
                command=lambda:self.show_a_dates_tasks())
        self.prcb.grid(row=0, column=3)
        ToolTip.ToolTip(self.lstb, anchor='e', text="Process te changes")
        self.datedhandle = datepicker.DateData()
        self.dt = self.datedhandle.getDateDatadisp()
        dl=tk.Label(self.history_tl, text="Date", anchor='e', width=10)
        dl.grid(row=1,column=1)
        dl=tk.Label(self.history_tl, textvariable=self.dt, width=23, anchor='w')
        dl.grid(row=1,column=2)
    def datepicker_pop(self):
        self.datepicker_tl = tk.Toplevel(self.master)
        self.datepicker_tl.iconbitmap('digitalclock2.ico')
        ldate = datepicker.Calendar(self.datepicker_tl,self.datedhandle)
        self.lstb.config(state = tk.ACTIVE  )
        if self.listshowed == True:
            
            self.tasklistrows = []
            self.listshowed = False
        self.datepicker_tl.grab_set()
    def show_a_dates_tasks(self):
        self.listshowed = True
        self.lstb.config(state = tk.DISABLED  )
        svardt = self.dt.get()
        dt = svardt[0:10]
        yr = dt[0:4]
        tasks = PCT_TimeDB.PCT_TimeDB.get_history_tasks(self.DB_Handle,dt,yr)
        for ix,row in enumerate(tasks):
            print(ix,row)

        """
http://www.color-hex.com/

"""            
            