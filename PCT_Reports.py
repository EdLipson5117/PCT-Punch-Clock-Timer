import tkinter as tk
import PCT_PunchClock as punchclock
import PCT_DB as PCT_TimeDB
import helper_ToolTip as ToolTip
from datetime import datetime, date, timedelta
import math
import os
import logging
import textwrap
# import operator


class PCT_Reports(tk.Frame):

    def __init__(self, master=None):
        self.master = master
        self.DB_Handle = None
        self.holdrtl = None
        self.quitphoto = None
        self.rqb = None
        self.pct = None
        self.wkday = [None, "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def last_week_report(self, pct, dbh):
        self.DB_Handle = dbh
        self.pct = pct
        curdt = datetime.today()
        cwkdat = curdt.weekday()
        sundt = curdt - timedelta(days=(cwkdat + 1))
        mondt = sundt - timedelta(days=6)
        tuedt = sundt - timedelta(days=5)
        weddt = sundt - timedelta(days=4)
        thudt = sundt - timedelta(days=3)
        fridt = sundt - timedelta(days=2)
        satdt = sundt - timedelta(days=1)
        mond = str(mondt.date())
        weekdates = [str(mondt.date()), str(tuedt.date()), str(weddt.date()), str(thudt.date()),
                     str(fridt.date()), str(satdt.date()), str(sundt.date())]
        self.display_report(weekdates, "The Previous Week's Time Report")

    def this_week_report(self, pct, dbh):
        self.DB_Handle = dbh
        self.pct = pct
        curdt = datetime.today()
        cwkdat = curdt.weekday()
        sundt = curdt - timedelta(days=(cwkdat + 1))
        sundt = sundt + timedelta(days=7)
        mondt = sundt - timedelta(days=6)
        tuedt = sundt - timedelta(days=5)
        weddt = sundt - timedelta(days=4)
        thudt = sundt - timedelta(days=3)
        fridt = sundt - timedelta(days=2)
        satdt = sundt - timedelta(days=1)
        weekdates = [str(mondt.date()), str(tuedt.date()), str(weddt.date()), str(thudt.date()),
                     str(fridt.date()), str(satdt.date()), str(sundt.date())]
        self.display_report(weekdates, "The Current Week's Time Report")

    def display_report(self, weekdates, wtitle):
        rptdata = PCT_TimeDB.PCT_TimeDB.generate_report(
            self.DB_Handle, weekdates)
        c0 = "#DDD5D5"
        c1 = "#C9C2C2"
        colr = True
        rptdict = {}
        for onerow in rptdata:
            (tim, dt, srt, nm) = onerow
            ix = weekdates.index(dt) + 1
            srtn = int(srt)
            timn = int(tim)
            if nm in rptdict:
                num = rptdict[nm]
                num[ix] = timn
                num[8] = num[1] + num[2] + num[3] + \
                    num[4] + num[5] + num[6] + num[7]
                rptdict[nm] = num
            else:
                num = [srtn, 0, 0, 0, 0, 0, 0, 0, 0]
                num[ix] = timn
                num[8] = num[1] + num[2] + num[3] + \
                    num[4] + num[5] + num[6] + num[7]
                rptdict[nm] = num
        self.holdrtl = tk.Toplevel(self.pct)
        self.holdrtl.title(wtitle)
        self.holdrtl.iconbitmap('digitalclock2.ico')
        self.quitphoto = tk.PhotoImage(file='log_off.gif')
        self.rqb = tk.Button(self.holdrtl, image=self.quitphoto,
                             command=lambda lltl=self.holdrtl: punchclock.PCT_PunchClock.popupquit(self.pct, lltl))
        r = 0
        c = 0
        self.rqb.grid(row=r, column=c)
        ToolTip.ToolTip(self.rqb, anchor='e', text="Leave the window")
        r += 1
        for dt in weekdates:
            c += 1
            daywk = dt + '\n' + self.wkday[c]
            tk.Label(self.holdrtl, text=daywk, width=10, anchor='w').grid(
                row=r, column=c)
        c += 1
        tk.Label(self.holdrtl, text='Lawyer Total\nReal Total',
                 width=10, anchor='w').grid(row=r, column=c)
        lablen = PCT_TimeDB.PCT_TimeDB.get_max_label_len(self.DB_Handle)
        dayrtot = [0, 0, 0, 0, 0, 0, 0, 0]
        dayltot = [0, 0, 0, 0, 0, 0, 0, 0]
        for drk, drv in sorted(rptdict.items(), key=lambda i: i[1][0]):
            r += 1
            c = 0
            tk.Label(self.holdrtl, text=drk, width=lablen, anchor='w').grid(
                row=r, column=c)
            for tim in drv[1:]:
                daytotix = c
                c += 1
                tenthtime = round(math.ceil(tim / (360)) / 10, 1)
                if c == len(dayltot):
                    dtim = str(tenthtime) + '/' + \
                        "{:03.2f}".format(tim / 3600.0)
                    tk.Label(self.holdrtl, text=dtim, width=10, anchor='w').grid(
                        row=r, column=c)
                else:
                    colr = False if colr else True
                    tk.Label(self.holdrtl, text=str(
                        tenthtime), width=10, anchor='w', bg=c0 if colr else c1).grid(row=r, column=c)
                dayrtot[daytotix] = dayrtot[daytotix] + tim
                dayltot[daytotix] = dayltot[daytotix] + tim
        r += 1
        c = 0
        tk.Label(self.holdrtl, text='Lawyer Total\nReal Total',
                 width=lablen, anchor='w').grid(row=r, column=c)
        for ttim in dayltot:
            c += 1
            rix = c - 1
            tenthtime = round(math.ceil(ttim / (360)) / 10, 1)
            dtim = str(tenthtime) + '/' + \
                "{:03.2f}".format(dayrtot[rix] / 3600.0)
            tk.Label(self.holdrtl, text=dtim, width=10, anchor='w').grid(
                row=r, column=c)

    def date_task(self, pct, dbhn, dbht):
        logging.info("REPORT Date Task Report")
        fh = self.notes_setup(pct, dbhn, dbht, "datetask")
        rdata = dbhn.getNotesby(self.todaydt, self.limitdt, dbht, 'D')
        self.notes_write(fh, rdata, dbhn, 'D')

    def task_date(self, pct, dbhn, dbht):
        logging.info("REPORT Task Date Report")
        fh = self.notes_setup(pct, dbhn, dbht, "taskdate")
        rdata = dbhn.getNotesby(self.todaydt, self.limitdt, dbht, 'T')
        self.notes_write(fh, rdata, dbhn, 'T')

    def notes_write(self, fh, rdata, dbhn, rpttype):
        for row in rdata:
            rptlines = textwrap.wrap(row[2])
            if rpttype == 'T':
                fh.write('Task name [' + row[0] + '] Date [' + row[1] + ']\n')
            else:
                fh.write('Date [' + row[1] + '] Task name [' + row[0] + ']\n')
            for line in rptlines:
                fh.write(line + '\n')
            fh.write('\n')
        fh.close()
        dbhn.release_db()

    def notes_setup(self, pct, dbhn, dbht, rpt):
        self.rptwks = int(dbht.get_config_item('NOTESREPORTWKS'))
        self.todaydt = str(date.today().isoformat())
        self.limitdt = str(
            (date.today() + timedelta(days=-(self.rptwks * 7))).isoformat())
        self.rptnum = int(dbht.get_config_item('REPORTNUM'))
        self.rptloc = dbht.get_config_item('REPORTLOC')
        p = dbht.cleandict['.rpt']
        dirlist = os.listdir(path=p)
        whatlist = [l for l in dirlist if '.rpt' in l]
        ctr = 0
        for item in sorted(whatlist, reverse=True):
            ctr += 1
            if ctr > self.rptnum:
                item = os.path.join(p, item)
                msg = "what " + '.rpt' + " deleting " + item
                logging.info(msg)
                os.remove(item)
        rptdt = datetime.today().strftime('%Y%m%d%H%M%S')
        rptfile = rpt + '_' + rptdt + '.rpt'
        self.report = os.path.join(p, rptfile)
        dbhn.conn_db('R', dbht)
        return open(self.report, 'w')

"""
http://www.color-hex.com/

"""
