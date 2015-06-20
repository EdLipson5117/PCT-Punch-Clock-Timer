
import calendar
import tkinter as tk
# import datetime
from datetime import datetime, date, timedelta
import time as time


class DateData:

    def __init__(self):
        self.day_selected = datetime.today().strftime('%d')
        self.month_selected = datetime.today().strftime('%m')
        self.year_selected = datetime.today().strftime('%Y')
        self.day_name = datetime.today().strftime('%A')
        self.dispdt = tk.StringVar()
        self.dispdt.set(self.year_selected + '-' + self.month_selected +
                        '-' + self.day_selected + ' is ' + self.day_name)

    def getDateDatadisp(self):
        return self.dispdt

    def getDateData(self):
        return self.year_selected + '-' + self.month_selected + '-' + self.day_selected

    def datedataset(self, year_selected, month_selected, day_selected, day_name):
        yyyy = str(year_selected)
        mm = str(month_selected)
        if len(mm) == 1:
            mm = '0' + mm
        dd = str(day_selected)
        if len(dd) == 1:
            dd = '0' + dd
        self.dispdt.set(yyyy + '-' + mm + '-' + dd + ' is ' + day_name)


class Calendar:

    def __init__(self, parent, data):
        self.data = data
        self.parent = parent
        self.cal = calendar.TextCalendar(calendar.SUNDAY)
        self.year = int(datetime.today().strftime('%Y'))
        self.month = int(datetime.today().strftime('%m'))
        self.wid = []
        self.day_selected = int(datetime.today().strftime('%d'))
        self.month_selected = self.month
        self.year_selected = self.year
        self.day_name = ''

        self.setup(self.year, self.month)

    def clear(self):
        for w in self.wid[:]:
            w[0].grid_forget()
            w[0].destroy()
            self.wid.remove(w)
        # self.parent.destroy()

    def go_prev(self):
        if self.month > 1:
            self.month -= 1
        else:
            self.month = 12
            self.year -= 1
        self.selected = (self.month, self.year)
        self.clear()
        self.setup(self.year, self.month)

    def go_next(self):
        if self.month < 12:
            self.month += 1
        else:
            self.month = 1
            self.year += 1

        self.selected = (self.month, self.year)
        self.clear()
        self.setup(self.year, self.month)

    def selection(self, day):
        self.day_selected = day
        self.month_selected = self.month
        self.year_selected = self.year
        self.day_name = time.strftime("%A", time.strptime(
            str(day) + ' ' + str(self.month) + ' ' + str(self.year), "%d %m %Y"))
        self.data.datedataset(
            self.year_selected, self.month_selected, self.day_selected, self.day_name)

        self.selected = day
        self.clear()
        self.parent.destroy()
        return [self.day_selected, self.month_selected, self.year_selected]

    def setup(self, y, m):
        left = tk.Button(self.parent, text='<', command=self.go_prev)
        self.wid.append([left, None])
        left.grid(row=0, column=1)

        header = tk.Label(
            self.parent, height=2, text='{}   {}'.format(calendar.month_abbr[m], str(y)))
        self.wid.append([header, None])
        header.grid(row=0, column=2, columnspan=3)

        right = tk.Button(self.parent, text='>', command=self.go_next)
        self.wid.append([right, None])
        right.grid(row=0, column=5)

        days = ['Sunday', 'Monday', 'Tuesday',
                'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for num, name in enumerate(days):
            t = tk.Label(self.parent, text=name[:3])
            self.wid.append([t, None])
            t.grid(row=1, column=num)

        for w, week in enumerate(self.cal.monthdayscalendar(y, m), 2):
            for d, day in enumerate(week):
                if day:
                    # print(calendar.day_name[day])
                    lstate = 'normal'
                    lrelief = 'raised'
                    lbg = 'white'
                    if day == self.day_selected:
                        lstate = 'active'
                        lrelief = 'sunken'
                        lbg = 'cyan'
                    b = tk.Button(self.parent, width=1, text=day,
                                  command=lambda day=day: self.selection(day))
                    self.wid.append([b, 'Date'])
                    b.grid(row=w, column=d)
                    b.config(state=lstate, relief=lrelief, bg=lbg)
        self.cal = calendar.TextCalendar(calendar.SUNDAY)

        sel = tk.Label(self.parent, height=2, text='{} {} {} {}'.format(
            self.day_name, calendar.month_name[self.month_selected], self.day_selected, self.year_selected))
        self.wid.append([sel, None])
        sel.grid(row=8, column=0, columnspan=7)

        # quit = tk.Button(self.parent, width=5, text='Cancel', command='disabled')
        quit = tk.Button(
            self.parent, width=5, text='Cancel', command=lambda: self.parent.destroy())
        self.wid.append([quit, None])
        quit.grid(row=9, column=2, columnspan=3, pady=10)

# def win(parent, d):
    # win = tk.Toplevel(parent)
    # cal = Calendar(win, d)
# def quit(parent):
    # parent.destroy()

# data = DateData()
# root = tk.Tk()
# tk.Button(root, text='calendar', command=lambda:win(root, data)).grid()
# tk.Button(root, text='quit', command=lambda:quit(root)).grid()

# root.mainloop()

# print("data ",data.__dict__)
# print(DateData.getDateData(data))
