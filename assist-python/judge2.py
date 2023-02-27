import sys,os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import *

import sqlite3
from pathlib import Path
import time
import datetime

import subprocess
import time

# taskテーブルのインデックスが全て連番でないとkadaiidentifyが正しく動かない
kadaiidentify = 0 #課題識別用。0：取組中の課題，1～：データベースに入れた順
seitoidentify = "" #生徒識別用。
status_identify = ""
narabi = 0 #学習者リスト並び変え用
mushi = "1"
mush = 0 #mushが1ならmushi日以前のデータを無視

path = Path(__file__).parent   # 現在のディレクトリ
path /= '../'     # ディレクトリ移動
path_str = str(Path(path.resolve()))
# sql_path = path_str + '/assist.sqlite3'
# sql_path = path_str + '/test3.sqlite3'
# sql_path = path_str + '/expt.sqlite3'
sql_path = path_str + '/expt0218.sqlite3'
img_path = path_str + '/img'

#標準入力テスト用

answer_path = path_str + '/task-program/te-answer.c'
answerexe_path = path_str + '/task-program/te-answer.exe'
answercmd_path = path_str + '/task-program/te-answer'
input_path = path_str + '/task-program/te-input.c'
inputexe_path = path_str + '/task-program/te-input.exe'
inputcmd_path = path_str + '/task-program/te-input'

conn = sqlite3.connect(sql_path)
c = conn.cursor()

# historyテーブルを基に躓き判定
def judge():
    testcheck_flag = 0
    c.execute("select student_id from student")
    student_list = c.fetchall()
    c.execute("select task_id from task")
    task_list = c.fetchall()

    for i in student_list:
        for n in task_list:
            c.execute("select * from history where student_id=? and task_id=?", (i[0],n[0]))
            history_list = c.fetchall()
            c.execute("select *from status where student_id=? and task_id=?", (i[0],n[0]))
            status = c.fetchone()
            if len(history_list)>0: #history_listの要素数が3以上なら
                #手法Aはじまり
                count = len(history_list)
                for s in range(count):
                    now_time = history_list[s][3]
                    display_time = now_time[0:4] + "/" + now_time[4:6] + "/" + now_time[6:8] + " " +now_time[8:10] + ":" + now_time[10:12] + ":" + now_time[12:14]
                    c.execute("select *from status2 where student_id=? and task_id=? and history_id=?", (i[0],n[0],history_list[s][0]))
                    status2 = c.fetchone()

                    if s>=2:
                        if history_list[s][4] == 1 & history_list[s-1][4] == 1 & history_list[s-2][4] == 1:
                            c.execute("select answer_code,sim_old,sim_jaro,sim_dc,sim_sc,sim_ted,sim_to from history where history_id=?", (history_list[s][0],))
                            input_code = c.fetchall()
                            print(input_code)
                            old = input_code[-1][1]
                            jaro = input_code[-1][2]
                            dc = input_code[-1][3]
                            sc = input_code[-1][4]
                            ted = input_code[-1][5]
                            to = input_code[-1][6]

                            c.execute("select answer_code,sim_old,sim_jaro,sim_dc,sim_sc,sim_ted,sim_to from history where history_id=?", (history_list[s-2][0],))
                            input_code2 = c.fetchall()
                            old2 = input_code2[-1][1]
                            jaro2 = input_code2[-1][2]
                            dc2 = input_code2[-1][3]
                            sc2 = input_code2[-1][4]
                            ted2 = input_code2[-1][5]
                            to2 = input_code2[-1][6]

                            if old2-old>0:
                                error_flag=-2
                            else:
                                error_flag = -1
                        else:
                            error_flag = 0


                        if status2: #既にstudent_idとtask_idのstatusが保存されているなら，レコード編集
                            a = (error_flag, s+1,display_time, i[0],n[0],history_list[s][0])
                            c.execute("update status2 SET status_flag=?, count=?, judge_time=? where  student_id=? and task_id=? and history_id=?", a)
                            conn.commit()
                        else: #まだstudent_idとtask_idのstatusが保存されていなければ，新規レコード
                            a = (i[0],n[0], history_list[s][0],error_flag, s+1,display_time)
                            c.execute("insert into status2 (student_id,task_id,history_id,status_flag,count,judge_time) values(?,?,?,?,?,?)", a)
                            conn.commit()
                    elif s>=0:
                        if status2: #既にstudent_idとtask_idのstatusが保存されているなら，レコード編集
                            a = (0, s+1,display_time, i[0],n[0],history_list[s][0])
                            c.execute("update status2 SET status_flag=?, count=?, judge_time=? where  student_id=? and task_id=? and history_id=?", a)
                            conn.commit()

                        else: #まだstudent_idとtask_idのstatusが保存されていなければ，新規レコード
                            a = (i[0],n[0], history_list[s][0],0, s+1,display_time)
                            c.execute("insert into status2 (student_id,task_id,history_id,status_flag,count,judge_time) values(?,?,?,?,?,?)", a)
                            conn.commit()
                #手法Aはじまり
                # 手法Bはじまり
                count = len(history_list)
                for s in range(count):
                    now_time = history_list[s][3]
                    display_time = now_time[0:4] + "/" + now_time[4:6] + "/" + now_time[6:8] + " " +now_time[8:10] + ":" + now_time[10:12] + ":" + now_time[12:14]
                    c.execute("select *from statusB where student_id=? and task_id=? and history_id=?", (i[0],n[0],history_list[s][0]))
                    statusB = c.fetchone()

                    if s>=2:
                        if history_list[s][4] == 1:
                            c.execute("select history_id from history where error_flag=1")
                            error_count = c.fetchall()
                            print(error_count)
                            print(len(error_count))
                            if(len(error_count)>=3):

                                c.execute("select answer_code,sim_old,sim_jaro,sim_dc,sim_sc,sim_ted,sim_to from history where history_id=?", (history_list[s][0],))
                                input_code = c.fetchall()
                                old = input_code[-1][1]
                                jaro = input_code[-1][2]
                                dc = input_code[-1][3]
                                sc = input_code[-1][4]
                                ted = input_code[-1][5]
                                to = input_code[-1][6]

                                c.execute("select answer_code,sim_old,sim_jaro,sim_dc,sim_sc,sim_ted,sim_to from history where history_id=?", (history_list[s-2][0],))
                                input_code2 = c.fetchall()
                                old2 = input_code2[-1][1]
                                jaro2 = input_code2[-1][2]
                                dc2 = input_code2[-1][3]
                                sc2 = input_code2[-1][4]
                                ted2 = input_code2[-1][5]
                                to2 = input_code2[-1][6]

                            if old2-old>0:
                                error_flag=-2
                            else:
                                error_flag = -1
                        else:
                            error_flag = 0


                        if statusB: #既にstudent_idとtask_idのstatusが保存されているなら，レコード編集
                            a = (error_flag, s+1,display_time, i[0],n[0],history_list[s][0])
                            c.execute("update statusB SET status_flag=?, count=?, judge_time=? where  student_id=? and task_id=? and history_id=?", a)
                            conn.commit()
                        else: #まだstudent_idとtask_idのstatusが保存されていなければ，新規レコード
                            a = (i[0],n[0], history_list[s][0],error_flag, s+1,display_time)
                            c.execute("insert into statusB (student_id,task_id,history_id,status_flag,count,judge_time) values(?,?,?,?,?,?)", a)
                            conn.commit()
                    elif s>=0:
                        if statusB: #既にstudent_idとtask_idのstatusが保存されているなら，レコード編集
                            a = (0, s+1,display_time, i[0],n[0],history_list[s][0])
                            c.execute("update statusB SET status_flag=?, count=?, judge_time=? where  student_id=? and task_id=? and history_id=?", a)
                            conn.commit()

                        else: #まだstudent_idとtask_idのstatusが保存されていなければ，新規レコード
                            a = (i[0],n[0], history_list[s][0],0, s+1,display_time)
                            c.execute("insert into statusB (student_id,task_id,history_id,status_flag,count,judge_time) values(?,?,?,?,?,?)", a)
                            conn.commit()





judge()