import tkinter as tk
import PCT_PunchClock as punchclock
import PCT_Tasks as tasks
import PCT_Reports as reports
import PCT_Notes as notes
import PCT_History as history

class PCT_Menu(tk.Frame):
    def __init__(self, pct, master=None):
        self.DB_Handle = punchclock.PCT_PunchClock.get_timeDB_handle(pct)
        self.menubar = tk.Menu(master)
#Tasks
        self.taskmenu = tk.Menu(self.menubar, tearoff=0)
        self.taskmenu.add_command(label="Add Hidden Task for the Day", 
                command=lambda selfasltah = punchclock.PCT_PunchClock.get_taskshandle(pct), lpct = pct \
                :tasks.PCT_Tasks.display_hidden(selfasltah,lpct))
        self.taskmenu.add_command(label="Add New Task", 
                command=lambda selfasltah = punchclock.PCT_PunchClock.get_taskshandle(pct), lpct = pct, 
                ldbh = self.DB_Handle \
                :tasks.PCT_Tasks.add_new_task(selfasltah,lpct,ldbh))
        self.taskmenu.add_command(label="Edit Tasks", 
                command=lambda selfasltah = punchclock.PCT_PunchClock.get_taskshandle(pct), lpct = pct, 
                ldbh = self.DB_Handle \
                :tasks.PCT_Tasks.edit_tasks_list(selfasltah,lpct,ldbh))
# submenu for ordering tasks
        self.ordertasksmenu = tk.Menu(self.taskmenu, tearoff=0)
        self.ordertasksmenu.add_command(label="GUI Project Tasks", 
                command=lambda selfasltah = punchclock.PCT_PunchClock.get_taskshandle(pct), lpct = pct, 
                ldbh = self.DB_Handle \
                :tasks.PCT_Tasks.lb_order_tasks(selfasltah,lpct,ldbh,'GPT'))
        self.ordertasksmenu.add_command(label="GUI Misc Tasks", 
                command=lambda selfasltah = punchclock.PCT_PunchClock.get_taskshandle(pct), lpct = pct, 
                ldbh = self.DB_Handle \
                :tasks.PCT_Tasks.lb_order_tasks(selfasltah,lpct,ldbh,'GMS'))
        self.ordertasksmenu.add_command(label="Report All Tasks", 
                command=lambda selfasltah = punchclock.PCT_PunchClock.get_taskshandle(pct), lpct = pct, 
                ldbh = self.DB_Handle \
                :tasks.PCT_Tasks.lb_order_tasks(selfasltah,lpct,ldbh,'RPT'))
        self.taskmenu.add_cascade(label="Order Tasks", menu=self.ordertasksmenu)
# end of submenu
        self.taskmenu.add_command(label="Misc Task", 
                command=lambda selfasltah = punchclock.PCT_PunchClock.get_taskshandle(pct), lpct = pct, \
                ldbh = self.DB_Handle \
                :tasks.PCT_Tasks.misc_tasks_display(selfasltah,lpct,ldbh))
        self.menubar.add_cascade(label="Tasks", menu=self.taskmenu)
#reports
        self.reportmenu = tk.Menu(self.menubar, tearoff=0)
        self.reportmenu.add_command(label="Report on Last Week", 
                command=lambda lpct = pct, lrpt = reports.PCT_Reports(), ldbh = self.DB_Handle \
                :reports.PCT_Reports.last_week_report(lrpt,lpct,ldbh))
        self.reportmenu.add_command(label="Report on This Week", 
                command=lambda lpct = pct, lrpt = reports.PCT_Reports(), ldbh = self.DB_Handle \
                :reports.PCT_Reports.this_week_report(lrpt,lpct,ldbh))
#Notes Report submenu
        self.notesrptmenu = tk.Menu(self.taskmenu, tearoff=0)
        self.notesrptmenu.add_command(label="Task then Date", 
                command=lambda lpct = pct, lrpt = reports.PCT_Reports(), \
                ldbhn = punchclock.PCT_PunchClock.get_notesDB_handle(pct), ldbht = self.DB_Handle \
                :reports.PCT_Reports.task_date(lrpt,lpct,ldbhn,ldbht))
        self.notesrptmenu.add_command(label="Date then Task", 
                command=lambda lpct = pct, lrpt = reports.PCT_Reports(), \
                ldbhn = punchclock.PCT_PunchClock.get_notesDB_handle(pct), ldbht = self.DB_Handle \
                :reports.PCT_Reports.date_task(lrpt,lpct,ldbhn,ldbht))
        self.reportmenu.add_cascade(label="Notes", menu=self.notesrptmenu)
#end of submenu
        self.reportmenu.add_command(label="History", 
                command=lambda lpct = pct, lhis = history.PCT_History(), ldbh = self.DB_Handle \
                :history.PCT_History.historical_edit(lhis,lpct,ldbh))
        self.menubar.add_cascade(label="Reports", menu=self.reportmenu)
#Help
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About", command=lambda lpct = pct:punchclock.PCT_PunchClock.about(lpct))
        self.helpmenu.add_command(label="Update Configuration Options", 
                command=lambda selfasltah = punchclock.PCT_PunchClock.get_taskshandle(pct), lpct = pct, 
                ldbh = self.DB_Handle \
                :tasks.PCT_Tasks.edit_config_list(selfasltah,lpct,ldbh))
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        master.config(menu=self.menubar)

class PCT_RCTB_Menu(tk.Frame):
    def __init__(self,pct,master=None):
        self.master = master
        self.rctbself = self
        self.pct = pct
        self.widgetclicked = None
        self.notesdbh = None
        self.rcMenu = tk.Menu(self.master, tearoff=0)
        self.rcMenu.add_command(label="Move Time To/From", command=self.movetime)
        self.rcMenu.add_command(label="Adjust Time", command=self.adjusttime)
        self.rcMenu.add_command(label="Notes", command=self.editnote)
        punchclock.PCT_PunchClock.bind_rctb(pct,self.rctbself)
        self.DBT_Handle = punchclock.PCT_PunchClock.get_timeDB_handle(pct)
        self.DBN_Handle = punchclock.PCT_PunchClock.get_notesDB_handle(pct)
    def movetime(self):
        rctb_keys = punchclock.PCT_PunchClock.get_rctb_keys(self.pct,self.widgetclicked)
        task_handle = punchclock.PCT_PunchClock.get_taskshandle(self.pct)
        tasks.PCT_Tasks.movetasktime(task_handle,self.pct,self.DBT_Handle,rctb_keys) 
    def adjusttime(self):
        rctb_keys = punchclock.PCT_PunchClock.get_rctb_keys(self.pct,self.widgetclicked)
        task_handle = punchclock.PCT_PunchClock.get_taskshandle(self.pct)
        tasks.PCT_Tasks.adjusttasktime(task_handle,self.pct,self.DBT_Handle,rctb_keys)
    def editnote(self):
        rctb_keys = punchclock.PCT_PunchClock.get_rctb_keys(self.pct,self.widgetclicked)
        notes_handle = punchclock.PCT_PunchClock.get_noteshandle(self.pct)
        notes.PCT_Notes.editnote(notes_handle,self.pct,self.DBN_Handle,self.DBT_Handle,rctb_keys)
    def popup(self, event):
        self.rcMenu.post(event.x_root, event.y_root)
        self.widgetclicked = event.widget
