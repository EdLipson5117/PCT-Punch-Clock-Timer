import tkinter as tk
from datetime import datetime
import logging
import PCT_PunchClock as punchclock
import PCT_Menu as menu
import re
import profile


logdt = datetime.today().strftime('%Y%m%d%H%M%S')
logfile = 'PCTLog' + logdt + '.log'
logging.basicConfig(filename=logfile,level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s %(filename)s %(module)s %(funcName)s %(lineno)d')


root = tk.Tk()
root.title('PCT Punch Clock Timer')
root.iconbitmap('digitalclock2.ico')
pcthandle = punchclock.PCT_PunchClock(master=root)
root.wm_protocol("WM_DELETE_WINDOW",lambda:pcthandle.quit())
menuhandle = menu.PCT_Menu(pcthandle,master=root) 
rcmenuhandle = menu.PCT_RCTB_Menu(pcthandle,master=root) 
punchclock.PCT_PunchClock.setrctbselfinpct(pcthandle,rcmenuhandle)

pcthandle.mainloop()
# profile.run('pcthandle.mainloop()')
