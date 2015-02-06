PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE T_TASK_TIMELOG (
 [LOG_APPL_END_TM] char(8) 
,[LOG_WALL_END_TM] char(8) 
,[LOG_APPL_START_TM] char(8) NOT NULL
,[LOG_WALL_START_TM] char(8) NOT NULL
,[LOG_DT] char(10) NOT NULL
,[TIMELOG_ID] int PRIMARY KEY UNIQUE NOT NULL
);
CREATE TABLE "T_TASK_CONFIG"(
[CONFIG_NM_DESC_TX] Varchar(300)
,[CONFIG_VAL_CD] varchar(100)
,[CONFIG_NM] varchar(25) UNIQUE NOT NULL
,[CONFIG_ID] int PRIMARY KEY UNIQUE NOT NULL
);
INSERT INTO "T_TASK_CONFIG" VALUES('Number of database backups to keep','11','PCT_DB_bkup',0);
INSERT INTO "T_TASK_CONFIG" VALUES('Number of application logs to keep','7','.log',1);
INSERT INTO "T_TASK_CONFIG" VALUES('Length of a workday for your location','25200','DAYLEN',2);
INSERT INTO "T_TASK_CONFIG" VALUES('Database Version expected by code. Don''t change by hand','v0_009c','DBVERSION',3);
INSERT INTO "T_TASK_CONFIG" VALUES('X (left/right) coordinate where the window will be placed initially','1','XCOORD',4);
INSERT INTO "T_TASK_CONFIG" VALUES('Y (up/down) coordinate where the window will be placed initially','55','YCOORD',5);
INSERT INTO "T_TASK_CONFIG" VALUES('X (left/right) calculation base','130','XBASE',6);
INSERT INTO "T_TASK_CONFIG" VALUES('Y (up/down) calculation base','54','YBASE',7);
INSERT INTO "T_TASK_CONFIG" VALUES('X (left/right) calculation increment','7','XINCR',8);
INSERT INTO "T_TASK_CONFIG" VALUES('Y (up/down) calculation increment','43','YINCR',9);
INSERT INTO "T_TASK_CONFIG" VALUES('Tkinter After Cycle Time (loop speed)','737','AFTERTIME',10);
INSERT INTO "T_TASK_CONFIG" VALUES('Number of database backups to keep','3','PCT_NOTES_DB_bkup',11);
INSERT INTO "T_TASK_CONFIG" VALUES('Number of previous notes to show while editing today''s note','2','PREVNOTESSHOW',12);
INSERT INTO "T_TASK_CONFIG" VALUES('The upper limit for resetting the After loop speed in ms. (smaller value)','500','AFTERUPPER',13);
INSERT INTO "T_TASK_CONFIG" VALUES('The lower limit for resetting the After loop speed in ms. (larger value)','1200','AFTERLOWER',14);
INSERT INTO "T_TASK_CONFIG" VALUES('Minimum timelimit for using timelog entries (seconds))','3600','AFTERUSE',15);
INSERT INTO "T_TASK_CONFIG" VALUES('Width of the Notes edit window','120','NOTESWIDTH',16);
INSERT INTO "T_TASK_CONFIG" VALUES('Number of rows displayed in the Notes edit window','25','NOTESEDITROWS',17);
INSERT INTO "T_TASK_CONFIG" VALUES('Number of rows displayed in the previous Notes view window','6','NOTESVIEWROWS',18);
INSERT INTO "T_TASK_CONFIG" VALUES('Location for database backups','bkup\','BKUPLOC',19);
INSERT INTO "T_TASK_CONFIG" VALUES('Location for reports','reports\','REPORTLOC',20);
INSERT INTO "T_TASK_CONFIG" VALUES('Number of report files to keep','10','REPORTNUM',21);
INSERT INTO "T_TASK_CONFIG" VALUES('Number of weeks to include in the report, today back.','6','NOTESREPORTWKS',22);
CREATE TABLE [T_TASKS](
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
                );
INSERT INTO "T_TASKS" VALUES('2015',210,8,NULL,NULL,NULL,'Misc','Jury','MS',0);
INSERT INTO "T_TASKS" VALUES('2015',120,1,NULL,NULL,NULL,'Misc','Holiday','MS',1);
INSERT INTO "T_TASKS" VALUES('2015',130,4,NULL,NULL,NULL,'Misc','Sick','MS',2);
INSERT INTO "T_TASKS" VALUES('2015',140,2,NULL,NULL,NULL,'Misc','Vacation','MS',3);
INSERT INTO "T_TASKS" VALUES('2015',150,3,NULL,NULL,NULL,'Misc','Personal Day','MS',4);
INSERT INTO "T_TASKS" VALUES('2015',160,7,NULL,NULL,NULL,'Misc','Not in Bank','MS',5);
INSERT INTO "T_TASKS" VALUES('2015',170,5,NULL,NULL,NULL,'Misc','Carryover','MS',6);
INSERT INTO "T_TASKS" VALUES('2015',180,6,NULL,NULL,NULL,'Misc','Recognition','MS',7);
INSERT INTO "T_TASKS" VALUES('2015',190,9,NULL,NULL,NULL,'Misc','Volunteer','MS',8);
INSERT INTO "T_TASKS" VALUES('2015',200,10,NULL,NULL,NULL,'Misc','Death','MS',9);
CREATE TABLE "T_TASK_TIME"(
[TASK_TIME_DT] char(10) NOT NULL DEFAULT '2000-01-01'
,[TASK_TIME_NO] int NOT NULL DEFAULT 0
,[TASK_TYPE_CD] Char(2) NOT NULL
,[TASK_ID] int NOT NULL
,[TASKTIME_ID] int PRIMARY KEY UNIQUE NOT NULL
   
);
CREATE UNIQUE INDEX [I_TASK_TIME_DT_UK] On [T_TASK_TIME] (
                    [TASK_ID] ,
                    [TASK_TYPE_CD] ,
                    [TASK_TIME_DT] );
COMMIT;
