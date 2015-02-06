import tkinter as tk
import tkinter.messagebox
import sqlite3
from datetime import date, timedelta
import winsound
import logging
import PCT_DB as PCT_TimeDB
import PCT_Tasks as PCT_Tasks
import PCT_Notes as PCT_Notes
import helper_ToolTip as ToolTip
import PCT_Menu as menu

class PCT_PunchClock(tk.Frame):
    def __init__(self, master=None):
        # class instance defs
        self.master = master
        self.blist        = [] # list of buttons
        self.tlist        = [] # list of labels
        self.tasklist     = [] # list of tasks
        self.htasklist    = [] # list of hidden tasks
        self.timlist      = [] # list of times
        self.dtimlist     = [] # list of display times, StringVar
        self.runningix    = None # currently active index into lists
        self.afterid = None
        self.alarmcycletime = None
        self.alarmcountdown = 0
        self.totaltime = 0
        self.ttimel = None
        self.popuppopped = None
        self.buttons = []
        self.butphotos = []
        self.buttaskdict = {}
        self.rcmenuhandle = None
        # class instance initialization funtions
        self.f=tk.Frame.__init__(self, self.master)
        self.taskshandle = PCT_Tasks.PCT_Tasks(self.master)
        self.noteshandle = PCT_Notes.PCT_Notes(self.master)
        self.addbuttons()
        self.PCTT = PCT_TimeDB.PCT_TimeDB()
        self.PCTN = PCT_TimeDB.PCT_NotesDB()
        self.build_tasklists()
        self.max_but_len = self.PCTT.get_max_but_len()
        self.build_task_display()
        totaltimemsg = 'Starting Total time is ' + str(timedelta(seconds=self.totaltime)) + ' or ' + str(self.totaltime)
        logging.info(totaltimemsg)
        self.auto_start()
        self.update_runningcounter()
    def setrctbselfinpct(self,rcmenuhandle):
        self.rcmenuhandle = rcmenuhandle
        return self.rcmenuhandle
    def getrctbselfinpct(self,rcmenuhandle):
        return self.rcmenuhandle
    def adjust_geo(self,rows):
        hcalc = ((rows-2) * 50) + 60
        wcalc = (self.max_but_len * 7) + 130
        newgeo=str(wcalc) + 'x' + str(hcalc) + '+1+55' 
        oldgeo = self.master.wm_geometry()
        logging.info("GEO old " + oldgeo + " new " + newgeo + " max but len " + str(self.max_but_len))
        # self.master.geometry(newgeo)
    def get_rctb_keys(self,but):
        return self.buttaskdict[but]
    def get_timeDB_handle(self):
        return self.PCTT
    def get_notesDB_handle(self):
        return self.PCTN
    def get_tasklists(self):
        return[self.tasklist,self.htasklist,[self.max_but_len]]
    def set_tasklists(self,lists):
        newtasks = lists[2][0]
        newix = len(self.tasklist) - newtasks
        self.display_tasks(newix+2,self.tasklist[newix:])
    def addbuttons(self)  :
        self.butphotos.append(tk.PhotoImage(file='log_off.gif'))
        b = tk.Button(self.f, image=self.butphotos[-1],anchor='w',command=self.quit)
        self.buttons.append(b)
        ToolTip.ToolTip(self.buttons[-1], anchor='e', text="Exit the application")
        self.butphotos.append(tk.PhotoImage(file='stop.gif'))
        b = tk.Button(self.f, image=self.butphotos[-1],anchor='e',command=self.stop)
        self.buttons.append(b)
        ToolTip.ToolTip(self.buttons[-1], anchor='e', text="Stop all of the timers")
        self.butphotos.append(tk.PhotoImage(file='silent.gif'))
        self.buttons.append(tk.Button(self.f, image=self.butphotos[-1],anchor='e',command=self.togglealarm))
        ToolTip.ToolTip(self.buttons[-1], anchor='e', text="Quiet Toggle of the Task alarm if one exists. Blue on, Yellow off, white none")
        c = -1
        for b in self.buttons:
            c += 1
            b.grid(row=0, column=c)
    def build_tasklists(self):
        for t in self.PCTT.getTasks():
    #    0    1     2    3    4    5     6     7     8     9   
    # (tid, ttid, pnm, tnm, tat, tash, tast, tsrt, ttim, tdt) = self.tasklist[ix]
            if t[5] == 1 or t[8] > 0:
                self.tasklist.append(t)
            else:
                self.htasklist.append(t)
    def stop(self):
        self.runningix = None
        self.reset_but()
        self.togglealarm()
    def get_noteshandle(self):
        return self.noteshandle
    def get_taskshandle(self):
        return self.taskshandle
    def togglealarm(self):
        if self.alarmcycletime != None:
            self.alarmcycletime = None
            self.alarmcountdown = 0
            if self.runningix != None:
                self.blist[self.runningix].config(bg='yellow')
        else: 
          if self.runningix != None:
                if self.tasklist[self.runningix][4] > 0:
                    self.alarmcycletime = self.tasklist[self.runningix][4]
                    self.alarmcountdown = self.tasklist[self.runningix][4]
                    self.blist[self.runningix].config(bg='cyan')
    def quit(self):
        self.PCTT.release_db(self.totaltime)
        self.master.after_cancel(self.afterid)
        self.master.update_idletasks()
        self.master.destroy()
        totaltimemsg = 'Ending Total time is ' + str(timedelta(seconds=self.totaltime)) + ' or ' + str(self.totaltime)
        logging.info(totaltimemsg)
    def auto_start(self):
        ix = -1
        for t in self.tasklist:
            ix += 1
        #    0    1     2    3    4    5     6     7     8     9   
            (tid, ttid, pnm, tnm, tat, tash, tast, tsrt, ttim, tdt) = t
            if tast == 1:
                adjustedix = ix + 2
                self.button_pop(adjustedix)
                break
    def alarm_check(self):
        if self.alarmcycletime != None:
            self.alarmcountdown -= 1
            if self.alarmcountdown < 1:
                self.alarmcountdown = self.alarmcycletime
                winsound.Beep(1000, 500);winsound.Beep(1200,400)
                # winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)
                if self.popuppopped == None:
                    t = tk.Toplevel(self)
                    t.wm_title("Task Time Check Alarm")
                    t.iconbitmap('digitalclock2.ico')
                    l1 = tk.Label(t, anchor='w', text="PCT Puch CLock Timer v0_003").grid(row=0, column=0)
                    l2 = tk.Label(t, anchor='w', text="Verify Active Task is Proper").grid(row=1, column=0)
                    self.popuppopped = tk.Button(t, text='Dismiss', command=lambda lt = t:self.popupquit(lt))
                    self.popuppopped.grid(row=10, column=0)
                    self.popuppopped.lift()
                    self.popuppopped.focus_set()
                    t.grab_set()
    def adjust_task_time(self,ix,atim):
        if ix == self.runningix:
            self.timlist[ix] += atim
            if self.timlist[ix] < 0:
                self.timlist[ix] = 0
        else:
            if self.timlist[ix] == 0:
                (tid, ttid, pnm, tnm, tat, tash, tast, tsrt, ttim, tdt) = self.tasklist[ix]
                new_ttid = self.PCTT.insert_task_time(tid,ttid)
                self.tasklist[ix] = (tid, new_ttid, pnm, tnm, tat, tash, tast, tsrt, atim if atim > 0 else 0, tdt)
                # self.tasklist[ix][1] = new_ttid
                # self.tasklist[ix][8] = atim if atim > 0 else 0
                self.timlist[ix] = self.tasklist[ix][8]
            else:
                self.timlist[ix] += atim
                if self.timlist[ix] < 0:
                    self.timlist[ix] = 0
            tim = self.timlist[ix]
            dtim = tk.StringVar()
            dtim.set(str(timedelta(seconds=tim)))
            self.dtimlist[ix] = dtim
            tdtim = str(timedelta(seconds=tim))
            self.tlist[ix].configure(text=tdtim)
            self.update_db_time(tim,ix)
    def update_db_time(self,tim,ix):
    #    0    1     2    3    4    5     6     7     8     9   
        (tid, ttid, pnm, tnm, tat, tash, tast, tsrt, ttim, tdt) = self.tasklist[ix]
        new_dt = date.today().isoformat()
        cur_dt = str(tdt)
        if new_dt != tdt or ttid < 0: # moved on to next day or no row, reset tables at ix
          new_id = self.PCTT.insert_task_time(tid,ttid)
          self.timlist[ix] = 0
          if new_dt != tdt:
            self.totaltime = 0
          self.tasklist[ix] = (tid, new_id, pnm, tnm, tat, tash, tast, tsrt, 0, new_dt)
        else:
          self.PCTT.update_task_time(tid,ttid,tim)
    def update_runningcounter(self):
        if self.runningix != None:
            ix = self.runningix
            tim = self.timlist[ix] + 1
            self.timlist[ix] = tim
            self.totaltime = self.sum_timlist()
            ttdtim = str(timedelta(seconds=self.totaltime))
            self.ttimel.configure(text=ttdtim)
            dtim = tk.StringVar()
            dtim.set(str(timedelta(seconds=tim)))
            self.dtimlist[ix] = dtim
            tdtim = str(timedelta(seconds=tim))
            self.tlist[ix].configure(text=tdtim)
            self.update_db_time(tim,ix)
            self.alarm_check()
        self.afterid = self.master.after(1000, self.update_runningcounter) # runs 8.55% slow at 1000 ms
    def reset_but(self):
        for b in self.blist:
            b.config(state = 'normal',relief = 'raised',bg='white')
    def button_pop(self,tr):
        self.reset_but()
        ltr = tr - 2
        self.runningix = ltr
        if self.tasklist[ltr][4] > 0:
            self.alarmcycletime = self.tasklist[ltr][4]
            self.alarmcountdown = self.tasklist[ltr][4]
            self.blist[self.runningix].config(bg='cyan')
        else:
            self.alarmcycletime = None
            self.alarmcountdown = 0
            self.blist[self.runningix].config(bg='white')
        self.blist[self.runningix].config(state = 'active',relief = 'sunken')
    def display_tasks(self,gridrow,list):
        for t in list:
            gridrow += 1
            n = t[2] + '\n' + t[3]
            nb = tk.Button(self.f, text=n, width=self.max_but_len, anchor='w', bg='white',
                command=lambda lr = gridrow - 1, lt = t[0]:self.button_pop(lr)  )
            nb.grid(row=gridrow, column=0)
            if self.rcmenuhandle != None:
                nb.bind("<Button-3>", self.rcmenuhandle.popup)
            self.blist.append(nb)
            bix = len(self.blist) - 1
            self.buttaskdict[nb] = [t[0],t[1],bix]
            dtim = tk.StringVar()
            dtim.set(str(timedelta(seconds=t[8])))
            tdtim = str(timedelta(seconds=t[8]))
            self.dtimlist.append(dtim)
            tl = tk.Label( self.f, text=tdtim, width=9, anchor='e')
            tl.grid(row=gridrow, column=1)
            self.tlist.append(tl)
            self.timlist.append(t[8])
        self.adjust_geo(gridrow)
    def build_task_display(self):
        gridrow = 1
        ttdtim = str(timedelta(seconds=self.totaltime))
        tl = tk.Label( self.f, text="Day's Total Time", anchor='w')
        tl.grid(row=gridrow, column=0)
        self.ttimel = tk.Label( self.f, text=ttdtim, width=9, anchor='e')
        self.ttimel.grid(row=gridrow, column=1)
        gridrow += 1
        self.display_tasks(gridrow,self.tasklist)
        self.totaltime = self.sum_timlist()
    def sum_timlist(self):
        tt = 0
        for t in self.timlist:
          tt += t
        return tt
    def about(self):
        t = tk.Toplevel(self)
        t.wm_title("About")
        t.iconbitmap('digitalclock2.ico')
        l1 = tk.Label(t, anchor='w', text="PCT Punch Clock Timer v0.010").grid(row=0, column=0)
        l2 = tk.Label(t, anchor='w', text="by Ed Lipson (edlipsongm@gmail.com)").grid(row=1, column=0)
        l3 = tk.Label(t, anchor='w', text="Concept from Project Clock").grid(row=2, column=0)
        l4 = tk.Label(t, anchor='w', text="  by David Keeffe @2000").grid(row=3, column=0)
        l5 = tk.Label(t, anchor='w', text="Licensed under Apache License 2.0").grid(row=4, column=0)
        bq = tk.Button(t, text='Dismiss',
            command=lambda lt = t:self.popupquit(lt))
        bq.grid(row=10, column=0)
        bq.focus_set()
        t.lift()
        t.grab_set()
        t.transient(self)
        t.wait_window(t)
    def popupquit(self,w):
        self.popuppopped = None
        w.destroy()
    def bind_rctb(self,rctbself):
        for but in self.blist:
            but.bind("<Button-3>", rctbself.popup)