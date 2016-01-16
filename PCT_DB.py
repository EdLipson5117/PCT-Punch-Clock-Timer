import sqlite3
from datetime import date, datetime, timedelta
import time
from pathlib import Path
import shutil
import os
import logging


class PCT_TimeDB:

    def __init__(self, master=None):
        self.dbnm = 'PCT_DB'
        self.timelog_key = None
        self.cur = None
        self.timeadjustok = True
        self.configdict = {}
        self.todaydt = str(date.today().isoformat())
        self.todayyr = str(date.today().strftime('%Y'))
        self.conn = self.conn_db()
        self.tasks = self.read_tasks('SH')

    def file_cleanup(self, what):
        p = self.cleandict[what]
        limit = self.get_config_item(what)
        dirlist = os.listdir(path=p)
        whatlist = [l for l in dirlist if what in l]
        ctr = 0
        for item in sorted(whatlist, reverse=True):
            ctr += 1
            if ctr > int(limit):
                item = os.path.join(p, item)
                msg = "what " + what + " deleting " + item
                logging.info(msg)
                os.remove(item)

    def get_config_item(self, key):
        try:
            return self.configdict[key]
        except:
            logging.warning("Could not find configuration item " + key)
            return None

    def add_config_item(self, key, val, desc):
        self.cur.execute("SELECT MAX(CONFIG_ID) + 1 from t_task_config")
        cid = int(self.cur.fetchone()[0])
        self.cur.execute("INSERT INTO T_TASK_CONFIG (CONFIG_ID, CONFIG_NM, CONFIG_VAL_CD, CONFIG_NM_DESC_TX) \
        values (?,?,?,?)", [cid, key, val, desc])
        self.load_config()

    def set_config_item(self, key, val, desc):
        self.cur.execute("update t_task_config set config_val_cd = ? ,config_nm_desc_tx = ?\
        where config_nm = ?", [val, desc, key])
        self.load_config()

    def get_config(self, which=None):
        if which == None:
            self.cur.execute(
                "select config_nm, config_val_cd, config_nm_desc_tx from t_task_config order by config_nm")
        else:
            self.cur.execute("select config_nm, config_val_cd, config_nm_desc_tx from t_task_config where config_nm = ?",
                             [which])
        return self.cur.fetchall()

    def load_config(self):
        self.configdict = {}
        self.cur.execute("select config_nm,config_val_cd from t_task_config")
        clist = self.cur.fetchall()
        for citem in clist:
            msg = "config " + citem[0] + " " + citem[1]
            logging.info(msg)
            self.configdict[citem[0]] = citem[1]
        self.validate_create_config_paths()

    def validate_create_config_paths(self):
        paths = []
        self.cleandict = {}
        paths.append(os.path.normcase(self.get_config_item('BKUPLOC')))
        self.cleandict['PCT_DB_bkup'] = paths[-1]
        self.cleandict['PCT_NOTES_DB_bkup'] = paths[-1]
        # logging starts before database opens, so in program directory
        self.cleandict['.log'] = '.'
        paths.append(os.path.normcase(self.get_config_item('REPORTLOC')))
        self.cleandict['.rpt'] = paths[-1]
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)

    def get_max_misctask_len(self):
        self.cur.execute("select coalesce(max(length(trim(task_nm))),10) from t_tasks where task_yr = ? and task_type_cd = ?",
                         [self.todayyr, 'MS'])
        maxlen = self.cur.fetchone()[0]
        return maxlen

    def get_misctask_nm(self):
        self.cur.execute("select task_nm, task_id from t_tasks where task_yr = ? and task_type_cd = ? order by task_sort_gui_no",
                         [self.todayyr, 'MS'])
        self.misctasks = self.cur.fetchall()
        return self.misctasks

    def getTaskName(self, tid):
        self.cur.execute(
            "SELECT trim(TASK_PROJ_NM) || '\n' || trim(TASK_NM) FROM T_TASKS \
          WHERE TASK_ID = ?", [tid])
        nm = self.cur.fetchall()
        return nm[0]

    def getTaskNamesp(self, tid):
        self.cur.execute(
            "SELECT trim(TASK_PROJ_NM) || ' ' || trim(TASK_NM) FROM T_TASKS \
          WHERE TASK_ID = ?", [tid])
        nm = self.cur.fetchall()
        return nm[0]

    def getallTasksrpt(self, opt):
        if opt == 'RPT':
            self.cur.execute(
                "SELECT trim(TASK_PROJ_NM) || ' ' || trim(TASK_NM), TASK_ID FROM T_TASKS \
              WHERE TASK_YR = ? AND TASK_ALWAYS_SHOW_CD IN (0,1) ORDER BY TASK_SORT_RPT_NO", [self.todayyr])
        else:
            type_cd = 'PT' if opt == 'GPT' else 'MS'
            self.cur.execute(
                "SELECT trim(TASK_PROJ_NM) || ' ' || trim(TASK_NM), TASK_ID FROM T_TASKS \
              WHERE TASK_TYPE_CD = ? and TASK_YR = ? AND TASK_ALWAYS_SHOW_CD IN (0,1) \
              ORDER BY TASK_SORT_GUI_NO", [type_cd, self.todayyr])
        tasks = self.cur.fetchall()
        return tasks

    def create_new_tasktime_row(self, tid, tcd, tdt, time):
        self.cur.execute(
            "select coalesce(max(tasktime_id) + 1,0) From t_TASK_TIME")
        new_ttid = self.cur.fetchone()[0]
        lnew_ttid = int(new_ttid)
        ltid = int(tid)
        ltime = int(time)
        self.cur.execute("insert into t_task_time (task_id,task_type_cd,tasktime_id,task_time_no,task_time_dt) values (?,?,?,?,?)",
                         (ltid, tcd, lnew_ttid, ltime, tdt))
        return lnew_ttid

    def update_tasktime_time(self, ttid, time):
        ltime = int(time)
        lttid = int(ttid)
        self.cur.execute(
            "update t_task_time set task_time_no = ? where tasktime_id = ?", (ltime, lttid))

    def delete_tasktime_row(self, ttid):
        lttid = int(ttid)
        self.cur.execute(
            "delete from t_task_time where tasktime_id = ?", [lttid])

    def get_history_tasks(self, hdate, hyear):
        self.cur.execute(
            "SELECT TT.TASKTIME_ID, T.TASK_ID, TT.TASK_TIME_NO, TT.TASK_TIME_DT, \
        T.TASK_TYPE_CD, T.TASK_NM, T.TASK_PROJ_NM, T.TASK_SORT_RPT_NO \
        FROM  \
        (SELECT TASK_ID, TASK_NM, TASK_PROJ_NM, TASK_SORT_RPT_NO, TASK_TYPE_CD \
        FROM T_TASKS WHERE TASK_YR = ?) T \
        LEFT OUTER JOIN \
        (SELECT TASKTIME_ID, TASK_TIME_NO, TASK_TIME_DT, TASK_ID \
        FROM T_TASK_TIME WHERE TASK_TIME_DT = ?) TT ON T.TASK_ID = TT.TASK_ID \
        ORDER BY T.TASK_SORT_RPT_NO",
            (hyear, hdate))
        htasks = self.cur.fetchall()
        return htasks

    def update_task_sort(self, opt, tid, srtno):
        if opt == 'RPT':
            self.cur.execute(
                "update t_tasks set task_sort_rpt_no = ? where task_id = ?", (srtno, tid))
        else:
            self.cur.execute(
                "update t_tasks set task_sort_gui_no = ? where task_id = ?", (srtno, tid))

    def update_task_time(self, ttid, ttno):
        self.cur.execute("update t_task_time set task_time_no =  \
            case when task_time_no + ttno > 0 then task_time_no + ttno else 0 end \
            where tasktime_id = ?",
                         (ttno, ttid))

    def getTask(self, tid):
        self.cur.execute(
            "SELECT TASK_ID, TASK_PROJ_NM, TASK_NM, \
        COALESCE(TASK_ALERT_TM,0), \
        COALESCE(TASK_ALWAYS_SHOW_CD,0), \
        COALESCE(TASK_AUTO_START_CD,0) FROM T_TASKS WHERE TASK_ID = ?", [tid])
        return self.cur.fetchone()

    def setTask(self, datalist):
        if int(datalist[3]) == 0:
            datalist[3] = None
        else:
            datalist[3] = int(datalist[3]) * 60
        # if datalist[4] == 'H':
            # datalist[4] = None
        # else:
            # datalist[4] = 1
        if datalist[4] == 'H':
            datalist[4] = 0
        elif datalist[4] == 'I':
            datalist[4] = 2
        else:
            datalist[4] = 1
        if datalist[5] == 'N':
            datalist[5] = None
        else:
            datalist[5] = 1
            # self.cur.execute("UPDATE T_TASKS SET TASK_AUTO_START_CD = ? WHERE TASK_YR = ?",[None,self.todayyr])
        self.cur.execute(
            "UPDATE T_TASKS SET \
        TASK_PROJ_NM = ?, \
        TASK_NM = ?, \
        TASK_ALERT_TM = ?, \
        TASK_ALWAYS_SHOW_CD = ?, \
        TASK_AUTO_START_CD = ? \
        WHERE TASK_ID = ?", datalist[1:] + [datalist[0]])
        self.tasks = self.read_tasks('SH')

    def setTaskProj(self, oldpnm, newpnm):
        self.cur.execute(
            "UPDATE T_TASKS SET TASK_PROJ_NM = ? \
        WHERE TASK_PROJ_NM = ? and TASK_YR = ?\
        ", [newpnm, oldpnm, self.todayyr])
        self.tasks = self.read_tasks('SH')

    def getTasks(self):
        #    0    1     2    3    4    5     6     7     8     9
        # (tid, ttid, pnm, tnm, tat, tash, tast, tsrt, ttim, tdt) = self.tasklist[ix]
        return self.tasks

    def getallTasks(self):
        #    0    1     2    3    4    5     6     7     8     9
        # (tid, ttid, pnm, tnm, tat, tash, tast, tsrt, ttim, tdt) = self.tasklist[ix]
        return self.read_tasks('SHI')
        
    def read_tasks(self,shi):
        if shi == 'SH':
            qu = "SELECT T.TASK_ID ,COALESCE(TT.TASKTIME_ID,-1)AS TASKTIME_ID ,trim(T.TASK_PROJ_NM) AS TASK_PROJ_NM ,trim(T.TASK_NM) AS TASK_NM ,COALESCE(T.TASK_ALERT_TM,0) AS TASK_ALERT_TM ,COALESCE(T.TASK_ALWAYS_SHOW_CD,0) AS TASK_ALAYS_SHOW_CD ,COALESCE(T.TASK_AUTO_START_CD,0) AS TASK_AUTO_START_CD ,T.TASK_SORT_GUI_NO ,COALESCE(TT.TASK_TIME_NO,0) AS TASK_TIME_NO ,COALESCE(TT.TASK_TIME_DT,?) AS TASK_TIME_DT FROM (SELECT TASK_ID, TASK_PROJ_NM, TASK_NM, TASK_ALERT_TM, TASK_ALWAYS_SHOW_CD, TASK_AUTO_START_CD, TASK_SORT_GUI_NO FROM T_TASKS WHERE TASK_TYPE_CD = ? AND TASK_YR = ? AND TASK_ALWAYS_SHOW_CD IN (0,1)) T LEFT OUTER join (SELECT TASK_ID, TASKTIME_ID, TASK_TIME_NO, TASK_TIME_DT FROM T_TASK_TIME WHERE TASK_TIME_DT = ?) TT ON T.TASK_ID = TT.TASK_ID ORDER BY T.TASK_SORT_GUI_NO, T.TASK_PROJ_NM, T.TASK_NM"
        else:
            qu = "SELECT T.TASK_ID ,COALESCE(TT.TASKTIME_ID,-1)AS TASKTIME_ID ,trim(T.TASK_PROJ_NM) AS TASK_PROJ_NM ,trim(T.TASK_NM) AS TASK_NM ,COALESCE(T.TASK_ALERT_TM,0) AS TASK_ALERT_TM ,COALESCE(T.TASK_ALWAYS_SHOW_CD,0) AS TASK_ALAYS_SHOW_CD ,COALESCE(T.TASK_AUTO_START_CD,0) AS TASK_AUTO_START_CD ,T.TASK_SORT_GUI_NO ,COALESCE(TT.TASK_TIME_NO,0) AS TASK_TIME_NO ,COALESCE(TT.TASK_TIME_DT,?) AS TASK_TIME_DT FROM (SELECT TASK_ID, TASK_PROJ_NM, TASK_NM, TASK_ALERT_TM, TASK_ALWAYS_SHOW_CD, TASK_AUTO_START_CD, TASK_SORT_GUI_NO FROM T_TASKS WHERE TASK_TYPE_CD = ? AND TASK_YR = ? AND TASK_ALWAYS_SHOW_CD IN (0,1,2)) T LEFT OUTER join (SELECT TASK_ID, TASKTIME_ID, TASK_TIME_NO, TASK_TIME_DT FROM T_TASK_TIME WHERE TASK_TIME_DT = ?) TT ON T.TASK_ID = TT.TASK_ID ORDER BY T.TASK_SORT_GUI_NO, T.TASK_PROJ_NM, T.TASK_NM"
        self.cur.execute(qu,(self.todaydt, 'PT', self.todayyr, self.todaydt))
        self.t = self.cur.fetchall()
        return self.t

    def copytasksforwardoneyear(self):
        nextyr = str(int(self.todayyr) + 1)
        lmsg = "Copying tasks forward to next year"
        logging.info(lmsg)
        lmsg = 'Starting year ' + \
            str(self.todayyr) + ' new year ' + str(nextyr)
        logging.info(lmsg)
        self.cur.execute("select count(*) from t_tasks Where task_yr = ?",
                         [nextyr])
        nextyrct = self.cur.fetchone()[0]
        if nextyrct > 0:
            lmsg = 'Next year tasks exist ' + str(nextyrct)
            logging.warning(lmsg)
        else:
            self.cur.execute("select max(task_id) from t_tasks")
            maxtaskid = self.cur.fetchone()[0]
            maxtaskid += 1
            self.cur.execute("Select TASK_YR+1, TASK_SORT_RPT_NO, TASK_SORT_GUI_NO, TASK_AUTO_START_CD, TASK_ALWAYS_SHOW_CD, TASK_ALERT_TM, TASK_PROJ_NM, TASK_NM, TASK_TYPE_CD From T_TASKS Where task_yr = ? and TASK_ALWAYS_SHOW_CD in (0,1) order by task_type_cd,task_sort_gui_no, task_proj_nm, task_nm",
                             [self.todayyr])
            tasks = self.cur.fetchall()
            for ix, task in enumerate(tasks):
                taskval = list(task)
                taskval.append(str(maxtaskid + ix))
                self.cur.execute("insert into t_tasks (TASK_YR, TASK_SORT_RPT_NO, TASK_SORT_GUI_NO, TASK_AUTO_START_CD, TASK_ALWAYS_SHOW_CD, TASK_ALERT_TM, TASK_PROJ_NM, TASK_NM, TASK_TYPE_CD, task_id) values(?,?,?,?,?,?,?,?,?,?)",
                                 taskval)
            else:
                lmsg = 'Starting taskid ' + \
                    str(maxtaskid) + ' number inserted ' + str(ix + 1)
                logging.info(lmsg)

    def getTasksReport(self):
        self.cur.execute("SELECT TASK_SORT_RPT_NO ,TASK_PROJ_NM ,TASK_NM ,TASK_ID \
        FROM T_TASKS WHERE TASK_TYPE_CD = ?", ['PT'])
        return self.cur.fetchall()

    def get_max_but_len(self):
        self.cur.execute("select coalesce(max(length(trim(task_nm))),10) \
            from t_tasks where task_yr = ? and task_type_cd = ?",
                         [self.todayyr, 'PT'])
        maxlent = self.cur.fetchone()[0]
        self.cur.execute("select coalesce(max(length(trim(task_proj_nm))),10) \
            from t_tasks where task_yr = ? and task_type_cd = ?",
                         [self.todayyr, 'PT'])
        maxlenp = self.cur.fetchone()[0]
        return maxlent if maxlent >= maxlenp else maxlenp

    def get_max_label_len(self):
        self.cur.execute("select coalesce(max(length(trim(task_nm))),10) from t_tasks where task_yr = ?",
                         [self.todayyr])
        maxlent = self.cur.fetchone()[0]
        self.cur.execute("select coalesce(max(length(trim(task_proj_nm))),10) from t_tasks where task_yr = ?",
                         [self.todayyr])
        maxlenp = self.cur.fetchone()[0]
        return maxlent if maxlent >= maxlenp else maxlenp

    def get_todaydt_time(self):
        self.cur.execute(
            "select coalesce(sum(task_time_no),0) from t_task_time where task_time_dt = ?", [self.todaydt])
        todaydt_sec = self.cur.fetchone()[0]
        return todaydt_sec

    def get_next_timelog_key(self):
        self.cur.execute(
            "select coalesce(max(timelog_id) + 1,0) from t_task_timelog")
        return int(self.cur.fetchone()[0])

    def update_task_timelog(self, tlid, ttno):
        self.cur.execute("update t_task_timelog set log_appl_end_tm = ?, log_wall_end_tm = ?  \
            where timelog_id = ?",
                         (ttno, datetime.now().time().strftime('%H:%M:%S'), tlid))
        curdt = datetime.today()
        purgedt = curdt - timedelta(days=90)
        self.cur.execute(
            "delete from t_task_timelog where log_dt < ?", [str(purgedt.date())])

    def adjust_aftertime_value(self):
        logging.info('AFTERTIME adjusting aftertime value for next time')
        current_aftertime = self.get_config_item('AFTERTIME')
        self.cur.execute("select log_appl_start_tm, log_appl_end_tm, log_wall_start_tm, log_wall_end_tm\
            from t_task_timelog where log_dt = ? and log_appl_end_tm is not null order by log_wall_start_tm",
                         [self.todaydt])
        times = self.cur.fetchall()
        FMT = '%H:%M:%S'
        total_appl_tm = 0
        total_wall_tm = 0
        last_appl_tm = 0
        after_use = int(self.get_config_item('AFTERUSE'))
        after_upper = int(self.get_config_item('AFTERUPPER'))
        after_lower = int(self.get_config_item('AFTERLOWER'))
        for walltime in times:
            logging.info(
                "APPSEC on db start end  " + str(walltime[0]) + ' ' + str(walltime[1]))
            logging.info(
                "WALLTIM on db start end  " + str(walltime[2]) + ' ' + str(walltime[3]))
            wallsecdiff = int((datetime.strptime(
                walltime[3], FMT) - datetime.strptime(walltime[2], FMT)).total_seconds())
            appsecdiff = int(walltime[1]) - int(walltime[0])
            logging.info("APPSEC diff in sec " + str(appsecdiff))
            logging.info("WALLTIM diff in sec " + str(wallsecdiff))
            if wallsecdiff > after_use:
                total_wall_tm += wallsecdiff
                total_appl_tm += appsecdiff
                last_appl_tm = appsecdiff
            else:
                logging.info(
                    "AFTERTIME skipping current difference time is less than 3600 seconds " + str(wallsecdiff))
        try:
            logging.info("CLOCKSLOW total appl time " + str(total_appl_tm))
            logging.info("CLOCKSLOW total wall time " + str(total_wall_tm))
            clockslow = float(total_appl_tm) / float(total_wall_tm)
            logging.info(
                "CLOCKSLOW clockslow ratio app/wall " + str(clockslow))
        except ZeroDivisionError:
            clockslow = 1
            logging.info("AFTERTIME not adjusted no wall time captured")
        new_aftertime = int(float(current_aftertime) * clockslow)
        logging.info(
            "AFTERTIME calculated clock difference " + str(total_wall_tm - total_appl_tm))
        logging.info("AFTERTIME total appl time seconds " + str(total_appl_tm))
        logging.info("AFTERTIME last appl time seconds " + str(last_appl_tm))
        logging.info("AFTERTIME total wall time seconds " + str(total_wall_tm))
        logging.info(
            "AFTERTIME current aftertime seconds " + str(current_aftertime))
        logging.info("AFTERTIME slowness ratio app/wall " + str(clockslow))
        logging.info("AFTERTIME new aftertime seconds " + str(new_aftertime))
        if last_appl_tm > after_use:
            if new_aftertime > after_upper and new_aftertime < after_lower:
                if self.timeadjustok:
                    logging.info("AFTERTIME updated to new value")
                    self.cur.execute("UPDATE T_TASK_CONFIG SET CONFIG_VAL_CD = ? \
                    WHERE CONFIG_NM = ?", [str(new_aftertime), "AFTERTIME"])
                    self.cur.execute("UPDATE T_TASK_CONFIG SET CONFIG_VAL_CD = ? \
                    WHERE CONFIG_NM = ?", [str(new_aftertime), "AFTERUSE"])
                else:
                    logging.warning("AFTERTIME Adjustment discarded as there was some break in time tracking")
            else:
                logging.warning("AFTERTIME new aftertime seconds " + str(new_aftertime) +
                                " out of bounds (' + after_upper + ' to ' + after_lower + '), not updated")

    def timeadjustok_false(self):
        logging.warning("AFTERTIME Adjustment will not be done, some time adjustment has been made and calculation will be wrong")
        self.timeadjustok = False
    

    def insert_task_timelog(self, tlid, ttno):
        self.cur.execute("insert into t_task_timelog (timelog_id,log_dt,log_wall_start_tm,log_appl_start_tm)  \
            values (?,?,?,?)",
                         (tlid, self.todaydt, datetime.now().time().strftime('%H:%M:%S'), ttno))

    def update_task_time(self, tid, ttid, tm):
        self.cur.execute(
            "update t_task_time set task_time_no = ? where task_id = ? and tasktime_id = ?", (tm, tid, ttid))

    def insert_task_time(self, tid, ttid, new_dt):
        if self.todaydt != new_dt:
            self.todaydt = new_dt
        self.cur.execute(
            "select tasktime_id From T_TASK_TIME where task_id = ? and task_time_dt = ?", (tid, self.todaydt))
        test_new_ttid = self.cur.fetchone()
        if test_new_ttid is None:
            self.cur.execute(
                "select coalesce(max(tasktime_id) + 1,0) From t_TASK_TIME")
            new_ttid = self.cur.fetchone()[0]
            self.cur.execute("insert into t_task_time (task_id,task_type_cd,tasktime_id,task_time_no,task_time_dt) values (?,?,?,?,?)",
                             (tid, 'PT', new_ttid, 0, self.todaydt))
        else:
            new_ttid = test_new_ttid[0]
        return new_ttid

    def insert_misc_task_time(self, tid, tim, dt):
        self.cur.execute(
            "select coalesce(max(tasktime_id) + 1,0) From t_TASK_TIME")
        new_ttid = self.cur.fetchone()[0]
        self.cur.execute("insert into t_task_time (task_id,task_type_cd,tasktime_id,task_time_no,task_time_dt) values (?,?,?,?,?)",
                         (tid, 'MS', new_ttid, tim, dt))

    def insert_task(self, tnm, pnm, at, ash, ast, sgui, srpt, yr):
        self.cur.execute("select coalesce(max(task_id) + 1,0) From T_TASKS")
        new_tid = self.cur.fetchone()[0]
        self.cur.execute("insert into t_tasks (task_id, task_type_cd, task_nm, task_proj_nm, task_alert_tm, \
                    task_always_show_cd, task_auto_start_cd, task_sort_gui_no, task_sort_rpt_no, task_yr) \
                    values (?,?,?,?,?,?,?,?,?,?)",
                         (new_tid, 'PT', tnm, pnm, at, ash, ast, sgui, srpt, yr))
        self.tasks = self.read_tasks('SH')
        return new_tid

    def conn_db(self):
        dbext = '.sql3'
        dbnm = self.dbnm
        dbbdt = date.today().strftime('%Y%m%d')
        dbbdt = datetime.today().strftime('%Y%m%d%H%M%S')
        db = dbnm + dbext
        self.conn = sqlite3.connect(
            db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.cur = self.conn.cursor()
        self.conn.isolation_level = None
        self.run_migrations('v0_009d')
        self.load_config()
        self.conn.close()
        dbbk = dbnm + '_bkup_' + dbbdt + dbext
        dbbkp = os.path.join(self.cleandict['PCT_DB_bkup'], dbbk)
        shutil.copy(db, dbbkp)
        self.conn = sqlite3.connect(
            db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        logging.info('Database connection ' + db)
        self.conn.isolation_level = None
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA journal_mode = 'MEMORY'")
        self.timelog_key = self.get_next_timelog_key()
        todaydt_time = self.get_todaydt_time()
        self.insert_task_timelog(self.timelog_key, todaydt_time)
        self.file_cleanup(self.dbnm + '_bkup')
        self.file_cleanup('.log')
        return self.conn

    def release_db(self, total_appl_tm):
        self.update_task_timelog(self.timelog_key, total_appl_tm)
        self.adjust_aftertime_value()
        logging.info('Database close')
        self.conn.close()

    def generate_report(self, weekdates):
        (m, t, w, r, f, a, u) = weekdates
        self.cur.execute("SELECT \
            TT.TASK_TIME_NO, TT.TASK_TIME_DT, T.TASK_SORT_RPT_NO,\
            T.TASK_PROJ_NM || '\n' || T.TASK_NM AS TASK_NM \
            FROM \
            T_TASKS T, T_TASK_TIME TT \
            WHERE \
            T.TASK_ID = TT.TASK_ID \
            AND TT.TASK_TIME_DT IN (?,?,?,?,?,?,?) \
            ORDER BY T.TASK_SORT_RPT_NO", (m, t, w, r, f, a, u))
        return self.cur.fetchall()

    def run_migrations(self, ver):
        logging.info('Database migration version in is ' + ver)
        lcur = self.conn.cursor()
        lcur.execute("SELECT MAX(CONFIG_ID) from T_TASK_CONFIG ")
        (pre7) = lcur.fetchone()
        if pre7[0] < 3:
            logging.info('Database migration pre version 7 method migration')
            lcur.executescript("""
                Begin Transaction;
                Create  TABLE [Temp_591950798](
                    [CONFIG_NM_DESC_TX] Varchar(300)
                    ,[CONFIG_VAL_CD] varchar(100)
                    ,[CONFIG_NM] varchar(25) UNIQUE NOT NULL
                    ,[CONFIG_ID] int PRIMARY KEY UNIQUE NOT NULL
                    ) ;
                Drop Table [T_TASK_CONFIG];
                Alter Table [Temp_591950798] Rename To [T_TASK_CONFIG];
                Commit Transaction;
                Begin Transaction;
                Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) 
                    values ( "Number of database backups to keep", "10", "bkup", 0);
                Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) 
                    values ( "Number of application logs to keep", "4", ".log", 1);
                Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) 
                    values ( "Length of a workday for your location", "25200", "DAYLEN", 2);
                Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) 
                    values ( "Lower limit for normal task ids. Misc. tasks use ids lower than this.", "10", "LOWERLIMITTID", 3);
                Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) 
                    values ( "X (left/right) coordinate where the window will be placed initially", "1", "XCOORD", 4);
                Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) 
                    values ( "Y (up/down) coordinate where the window will be placed initially", "55", "YCOORD", 5);
                Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) 
                    values ( "X (left/right) calculation base", "130", "XBASE", 6);
                Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) 
                    values ( "Y (up/down) calculation base", "54", "YBASE", 7);
                Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) 
                    values ( "X (left/right) calculation increment", "7", "XINCR", 8);
                Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) 
                    values ( "Y (up/down) calculation increment", "43", "YINCR", 9);
                Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) 
                    values ( "Tkinter After Cycle Time (loop speed)", "1000", "AFTERTIME", 10);
                Commit Transaction;            
            """)
        lcur.execute(
            "SELECT CONFIG_NM, CONFIG_VAL_CD from T_TASK_CONFIG WHERE CONFIG_ID = 3")
        (dbvernm, dbvercd) = lcur.fetchone()
        logging.info('Database version in is ' + dbvercd)
        # subsequent migration runs, need to check ver to dbvercd
        if dbvernm == 'DBVERSION':
            if dbvercd == 'v0_007' and ver == 'v0_007a':
                logging.info('moving to v0_007a ' + dbvercd + ' ' + ver)
                self.conn.isolation_level = 'DEFERRED'
                lcur.executescript("""
                drop INDEX if exists MAIN.[I_TASK_TIME_DT_UK] ;
                CREATE Unique INDEX MAIN.[I_TASK_TIME_DT_UK] On [T_TASK_TIME] (
                    [TASK_ID] ,
                    [TASK_TYPE_CD] ,
                    [TASK_TIME_DT] );
                """)
                self.conn.commit()
                self.conn.isolation_level = None
                lcur.execute("UPDATE T_TASK_CONFIG \
                SET CONFIG_VAL_CD = ?\
                WHERE CONFIG_ID = 3", [ver])
            if dbvercd == 'v0_007a' and ver == 'v0_009b':
                lcur.execute("UPDATE T_TASK_CONFIG \
                SET CONFIG_NM = ? \
                WHERE CONFIG_NM = ?", ['PCT_DB_bkup', 'bkup'])
                lcur.execute("select max(config_id) + 1 from t_task_config")
                nextid = lcur.fetchone()[0]
                lcur.execute(
                    "Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) \
                    values ( ?,?,?,? )", ["Number of database backups to keep", 3, 'PCT_NOTES_DB_bkup', nextid]
                )
                lcur.execute("select max(config_id) + 1 from t_task_config")
                nextid = lcur.fetchone()[0]
                lcur.execute(
                    "Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) \
                    values ( ?,?,?,? )", ["Number of previous notes to show while editing today's note", 2, 'PREVNOTESSHOW', nextid]
                )
                lcur.execute("UPDATE T_TASK_CONFIG \
                SET CONFIG_VAL_CD = ?\
                WHERE CONFIG_ID = 3", [ver])
            if dbvercd == 'v0_009b' and ver == 'v0_009c':
                lcur.execute("select max(config_id) + 1 from t_task_config")
                nextid = lcur.fetchone()[0]
                lcur.execute(
                    "Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) \
                    values ( ?,?,?,? )", ["The upper limit for resetting the After loop speed in ms. (smaller value)", 500, 'AFTERUPPER', nextid])
                lcur.execute("select max(config_id) + 1 from t_task_config")
                nextid = lcur.fetchone()[0]
                lcur.execute(
                    "Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) \
                    values ( ?,?,?,? )", ["The lower limit for resetting the After loop speed in ms. (larger value)", 1200, 'AFTERLOWER', nextid])
                lcur.execute("select max(config_id) + 1 from t_task_config")
                nextid = lcur.fetchone()[0]
                lcur.execute(
                    "Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) \
                    values ( ?,?,?,? )", ["Minimum timelimit for using timelog entries (seconds))", 3600, 'AFTERUSE', nextid])
                lcur.execute("select max(config_id) + 1 from t_task_config")
                nextid = lcur.fetchone()[0]
                lcur.execute(
                    "Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) \
                    values ( ?,?,?,? )", ["Width of the Notes edit window", 80, 'NOTESWIDTH', nextid])
                lcur.execute("select max(config_id) + 1 from t_task_config")
                nextid = lcur.fetchone()[0]
                lcur.execute(
                    "Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) \
                    values ( ?,?,?,? )", ["Number of rows displayed in the Notes edit window", 30, 'NOTESEDITROWS', nextid])
                lcur.execute("select max(config_id) + 1 from t_task_config")
                nextid = lcur.fetchone()[0]
                lcur.execute(
                    "Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) \
                    values ( ?,?,?,? )", ["Number of rows displayed in the previous Notes view window", 10, 'NOTESVIEWROWS', nextid])
                lcur.execute("select max(config_id) + 1 from t_task_config")
                nextid = lcur.fetchone()[0]
                lcur.execute(
                    "Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) \
                    values ( ?,?,?,? )", ["Location for database backups and logs", '.', 'BKUPLOC', nextid])
                lcur.execute("select max(config_id) + 1 from t_task_config")
                nextid = lcur.fetchone()[0]
                lcur.execute(
                    "Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) \
                    values ( ?,?,?,? )", ["Location for reports", '.', 'REPORTLOC', nextid])
                lcur.execute("select max(config_id) + 1 from t_task_config")
                nextid = lcur.fetchone()[0]
                lcur.execute(
                    "Insert Into [T_TASK_CONFIG] ([CONFIG_NM_DESC_TX],[CONFIG_VAL_CD],[CONFIG_NM],[CONFIG_ID]) \
                    values ( ?,?,?,? )", ["Number of report files to keep", 10, 'REPORTNUM', nextid])
                lcur.execute("UPDATE T_TASK_CONFIG \
                SET CONFIG_VAL_CD = ?\
                WHERE CONFIG_ID = 3", [ver])
            if dbvercd == 'v0_009c' and ver == 'v0_009d':
                logging.info('moving from ' + dbvercd + ' to ' + ver)
                lcur.execute("UPDATE T_TASKS SET TASK_ALWAYS_SHOW_CD = 0 WHERE TASK_ALWAYS_SHOW_CD is NULL")
                lcur.execute("UPDATE T_TASK_CONFIG \
                SET CONFIG_NM = ?, CONFIG_VAL_CD = ?, CONFIG_NM_DESC_TX = ? \
                WHERE CONFIG_ID = 3", ['DBVERSION', ver, "Database Version expected by code. Don't change by hand"])
                
        else:  # first migration runs
            logging.info('moving to v0_007 ' + dbvercd + ' ' + ver)
            self.conn.isolation_level = 'DEFERRED'
            lcur.executescript("""
            begin transaction;
            alter table t_tasks rename to O_TASKS;
            Create  TABLE MAIN.[T_TASKS](
                [TASK_YR] char(4) NOT NULL
                ,[TASK_SORT_RPT_NO] INt NOT NULL DEFAULT 0
                ,[TASK_SORT_GUI_NO] int NOT NULL DEFAULT 0
                ,[TASK_AUTO_START_CD] int
                ,[TASK_ALWAYS_SHOW_CD] int
                ,[TASK_ALERT_TM] int
                ,[TASK_PROJ_NM] varchar(50)
                ,[TASK_NM] varchar(50) NOT NULL
                ,[TASK_TYPE_CD] char(2) NOT NULL
                ,[TASK_ID] INt NOT NULL
                , Primary Key(TASK_TYPE_CD,TASK_ID)   
                ) ;
            Insert Into MAIN.[T_TASKS] ([TASK_YR],[TASK_SORT_RPT_NO],[TASK_SORT_GUI_NO],[TASK_AUTO_START_CD],[TASK_ALWAYS_SHOW_CD],[TASK_ALERT_TM],[TASK_PROJ_NM],[TASK_NM],[TASK_TYPE_CD],[TASK_ID]) 
                    Select [TASK_YR],[TASK_SORT_RPT_NO],[TASK_SORT_GUI_NO],[TASK_AUTO_START_CD],[TASK_ALWAYS_SHOW_CD],[TASK_ALERT_TM],[TASK_PROJ_NM],[TASK_NM],'MS',[TASK_ID] From MAIN.[O_TASKS] WHERE TASK_ID < 10;
            Insert Into MAIN.[T_TASKS] ([TASK_YR],[TASK_SORT_RPT_NO],[TASK_SORT_GUI_NO],[TASK_AUTO_START_CD],[TASK_ALWAYS_SHOW_CD],[TASK_ALERT_TM],[TASK_PROJ_NM],[TASK_NM],[TASK_TYPE_CD],[TASK_ID]) 
                    Select [TASK_YR],[TASK_SORT_RPT_NO],[TASK_SORT_GUI_NO],[TASK_AUTO_START_CD],[TASK_ALWAYS_SHOW_CD],[TASK_ALERT_TM],[TASK_PROJ_NM],[TASK_NM],'PT',[TASK_ID] From MAIN.[O_TASKS] WHERE TASK_ID > 10;
            alter table t_task_time rename to O_TASK_TIME;
            Create  TABLE MAIN.[T_TASK_TIME](
                [TASK_TIME_DT] char(10) NOT NULL DEFAULT '2000-01-01'
                ,[TASK_TIME_NO] int NOT NULL DEFAULT 0
                ,[TASK_TYPE_CD] Char(2) NOT NULL
                ,[TASK_ID] int NOT NULL
                ,[TASKTIME_ID] int PRIMARY KEY UNIQUE NOT NULL
                ) ;
            CREATE Unique INDEX MAIN.[I_TASK_TIME_DT_UK] On [T_TASK_TIME] (
                    [TASK_ID] ,
                    [TASK_TYPE_CD] ,
                    [TASK_TIME_DT] );
            Insert Into MAIN.[T_TASK_TIME] ([TASK_TIME_DT],[TASK_TIME_NO],[TASK_TYPE_CD],[TASK_ID],[TASKTIME_ID]) 
                    Select [TASK_TIME_DT],[TASK_TIME_NO],'PT',[TASK_ID],[TASKTIME_ID] From MAIN.[O_TASK_TIME]
                    WHERE TASK_ID > 10;
            Insert Into MAIN.[T_TASK_TIME] ([TASK_TIME_DT],[TASK_TIME_NO],[TASK_TYPE_CD],[TASK_ID],[TASKTIME_ID]) 
                    Select [TASK_TIME_DT],[TASK_TIME_NO],'MS',[TASK_ID],[TASKTIME_ID] From MAIN.[O_TASK_TIME]
                    WHERE TASK_ID < 10;
            drop table MAIN.[O_TASK_TIME];
            drop table MAIN.[O_TASKS];
            delete from t_task_timelog;
            commit transaction;
            """)
            self.conn.commit()
            self.conn.isolation_level = None
            lcur.execute("UPDATE T_TASK_CONFIG \
            SET CONFIG_NM = ?, CONFIG_VAL_CD = ?, CONFIG_NM_DESC_TX = ? \
            WHERE CONFIG_ID = 3", ['DBVERSION', ver, "Database Version expected by code. Don't change by hand"])


class PCT_NotesDB:

    def __init__(self, master=None):
        self.dbnm = 'PCT_NOTES_DB'
        self.cur = None
        self.conn = None
        self.conmode = None
        self.todaydt = str(date.today().isoformat())

    def setTaskNote(self, tid, dt, txt):
        self.cur.execute("insert or replace into t_task_notes \
            (TASK_ID, TASK_NOTE_DT, TASK_NOTE_TX) VALUES (?,?,?)",
                         [tid, dt, txt])

    def getNotesby(self, start_dt, end_dt, taskdbhandle, rpttype):
        self.cur.execute("Create  TEMP TABLE G_TASKS \
            ([TASK_SORT_RPT_NO] INt NOT NULL \
            ,[TASK_PROJ_NM] varchar(50) \
            ,[TASK_NM] varchar(50) NOT NULL \
            ,[TASK_ID] INt NOT NULL \
            , Primary Key(TASK_ID) \
            )")
        tasks = taskdbhandle.getTasksReport()
        for task in tasks:
            self.cur.execute(
                "INSERT INTO TEMP.G_TASKS (TASK_SORT_RPT_NO ,TASK_PROJ_NM ,TASK_NM ,TASK_ID) VALUES (?,?,?,?)", task)
        if rpttype == 'D':
            rpt = self.getNotesbyD(start_dt, end_dt)
        else:
            rpt = self.getNotesbyT(start_dt, end_dt)
        return rpt

    def getNotesbyD(self, start_dt, end_dt):
        self.cur.execute("select trim(gt.task_proj_nm) || ' ' || trim(gt.task_nm) as nm, tt.task_note_dt, tt.task_note_tx \
            from t_task_notes tt inner join temp.g_tasks gt on tt.task_id = gt.task_id \
            where tt.task_note_dt <= ? and tt.task_note_dt >= ?\
            order by tt.task_note_dt desc, gt.task_sort_rpt_no \
            ", [start_dt, end_dt])
        return self.cur.fetchall()

    def getNotesbyT(self, start_dt, end_dt):
        self.cur.execute("select trim(gt.task_proj_nm) || ' ' || trim(gt.task_nm) as nm, tt.task_note_dt, tt.task_note_tx \
            from t_task_notes tt inner join temp.g_tasks gt on tt.task_id = gt.task_id \
            where tt.task_note_dt <= ? and tt.task_note_dt >= ?\
            order by gt.task_sort_rpt_no, tt.task_note_dt desc \
            ", [start_dt, end_dt])
        return self.cur.fetchall()

    def getTaskNotes(self, tid, limit, start_dt=None):
        ltid = int(tid)
        lim = int(limit)
        dt = start_dt if start_dt != None else self.todaydt
        self.cur.execute("select task_id, task_note_dt, task_note_tx \
            from t_task_notes \
            where task_id = ? and task_note_dt = ?",
                         [ltid, dt])
        notetoday = self.cur.fetchone()
        if notetoday == None:
            notetoday = []
        self.cur.execute("select task_id, task_note_dt, task_note_tx \
            from t_task_notes \
            where task_id = ? and task_note_dt < ?\
            order by task_note_dt desc limit ?",
                         [ltid, dt, lim])
        notesprev = self.cur.fetchall()
        return notetoday, notesprev

    def file_cleanup(self, what, taskdbhandle):
        limit = taskdbhandle.get_config_item(what)
        p = taskdbhandle.cleandict[what]
        dirlist = os.listdir(path=p)
        whatlist = [l for l in dirlist if what in l]
        ctr = 0
        for item in sorted(whatlist, reverse=True):
            ctr += 1
            if ctr > int(limit):
                item = os.path.join(p, item)
                msg = "what " + what + " deleting " + item
                logging.info(msg)
                os.remove(item)

    def conn_db(self, mode, taskdbhandle):
        if self.conmode != mode and self.conn != None:
            self.release_db()
        self.conmode = mode
        dbnm = self.dbnm
        dbext = '.sql3'
        dbbdt = date.today().strftime('%Y%m%d')
        dbbdt = datetime.today().strftime('%Y%m%d%H%M%S')
        db = dbnm + dbext
        dbbk = dbnm + '_bkup_' + dbbdt + dbext
        dbbkp = os.path.join(taskdbhandle.cleandict['PCT_DB_bkup'], dbbk)
        if mode == 'U':
            shutil.copy(db, dbbkp)
            self.file_cleanup(self.dbnm + '_bkup', taskdbhandle)
        self.conn = sqlite3.connect(
            db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        logging.info('Database connection ' + db + ' mode ' + mode)
        self.conn.isolation_level = None
        self.cur = self.conn.cursor()
        return self.conn

    def release_db(self):
        logging.info('Database close')
        self.conn.close()
        self.conn = None
        self.cur = None
        self.conmode = None
