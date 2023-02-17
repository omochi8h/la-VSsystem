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
sql_path = path_str + '/expt.sqlite3'
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
            print(i,n)
            print(len(history_list))
            if len(history_list)>0: #history_listの要素数が3以上なら
                count = len(history_list)
                for s in range(count):
                    come = 's:' + str(s)
                    print(come)
                    now_time = history_list[s][3]
                    display_time = now_time[0:4] + "/" + now_time[4:6] + "/" + now_time[6:8] + " " +now_time[8:10] + ":" + now_time[10:12] + ":" + now_time[12:14]
                    c.execute("select *from status2 where student_id=? and task_id=? and history_id=?", (i[0],n[0],history_list[s][0]))
                    status2 = c.fetchone()

                    if s>=2:
                        if history_list[s][4] == 1 & history_list[s-1][4] == 1 & history_list[s-2][4] == 1:
                            error_flag = -1
                        else:
                            error_flag = 0


                        if status2: #既にstudent_idとtask_idのstatusが保存されているなら，レコード編集
                            a = (error_flag, s+1,display_time, i[0],n[0],history_list[s][0])
                            c.execute("update status2 SET status_flag=?, count=?, judge_time=? where  student_id=? and task_id=? and history_id=?", a)
                            conn.commit()
                            print('asdas')
                        else: #まだstudent_idとtask_idのstatusが保存されていなければ，新規レコード
                            a = (i[0],n[0], history_list[s][0],error_flag, s+1,display_time)
                            c.execute("insert into status2 (student_id,task_id,history_id,status_flag,count,judge_time) values(?,?,?,?,?,?)", a)
                            conn.commit()
                            print('okkamko')
                    elif s>=0:
                        if status2: #既にstudent_idとtask_idのstatusが保存されているなら，レコード編集
                            a = (0, s+1,display_time, i[0],n[0],history_list[s][0])
                            c.execute("update status2 SET status_flag=?, count=?, judge_time=? where  student_id=? and task_id=? and history_id=?", a)
                            conn.commit()
                            print('0okok')

                        else: #まだstudent_idとtask_idのstatusが保存されていなければ，新規レコード
                            a = (i[0],n[0], history_list[s][0],0, s+1,display_time)
                            c.execute("insert into status2 (student_id,task_id,history_id,status_flag,count,judge_time) values(?,?,?,?,?,?)", a)
                            conn.commit()
                            print('ok')




            # elif len(history_list)==2: #history_listの要素数が
            #     print()


            #     # # ここから標準入力テスト 68以降一旦コメントアウト
            #     # if history_list[-1][4] == 1: #直近のコンパイルが成功していたら(error_flag=1だったら)
            #     #     print("dummy")
            #     #     testcheck_flag = 1
            #     # #     # te-answer.c書き込み
            #     #     c.execute("select true_code,test_flag,test_input1,test_input2,test_output1,test_output2,test_output0 from task where task_id=?",(n[0],))
            #     #     task_testdetail = c.fetchall()
            #     #     test_flag = task_testdetail[0][1]
            #     #     test_input1 = task_testdetail[0][2]
            #     #     test_input2 = task_testdetail[0][3]
            #     #     test_output1 = task_testdetail[0][4]
            #     #     test_output2 = task_testdetail[0][5]
            #     #     test_output0 = task_testdetail[0][6]                  

            #     #     c.execute("select answer_code,sim_old,sim_jaro,sim_dc,sim_sc,sim_ted,sim_to from history where student_id=? and task_id=?", (i[0],n[0]))
            #     #     input_code = c.fetchall()
            #     #     old = input_code[-1][1]
            #     #     jaro = input_code[-1][2]
            #     #     dc = input_code[-1][3]
            #     #     sc = input_code[-1][4]
            #     #     ted = input_code[-1][5]
            #     #     to = input_code[-1][6]
                    
            #     #     #テスト比較用コンパイル
            #     #     if test_flag == '1':

            #     #         file = open(input_path, 'w', encoding='utf-8')
            #     #         file.write(input_code[-1][0])
            #     #         file.close()

            #     #         cmd = "clang -o " + inputexe_path + " " + input_path
            #     #         # コンパイルを実行、エラーメッセージを取得．標準入力が必要なら，第二引数にinput=inpを設定
            #     #         r1 = subprocess.run(cmd.split(),encoding='utf-8',stderr=subprocess.PIPE) 

            #     #         cmd = inputcmd_path
                        



            #     #         if test_input1 != None:
            #     #             try:
            #     #                 c1 = subprocess.run(cmd.split(),input=test_input1,encoding='utf-8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)  #プログラムを実行、出力及びエラーメッセージを取得
            #     #             except:
            #     #                 pass
            #     #             Outc1 = "予期せぬエラーが起きたようです。" #プログラム実行エラーとか，ctrl-cとか
            #     #             if c1.returncode == 1:  #プログラム異常終了
            #     #                 Outc1 = c1.stderr  #エラー内容
            #     #             elif c1.returncode == 0:  #プログラム正常終了
            #     #                 Outc1 = c1.stdout  #標準出力
            #     #                 if test_output1 == Outc1:
            #     #                     test1 = "test1OK"
            #     #                 else:
            #     #                     test1 = "test1NOT!!!!!"
            #     #             print(test1)
            #     #             print(test_output1)
            #     #             print(Outc1)
                            
            #     #         if test_input2 != None:
            #     #             try:
            #     #                 c2 = subprocess.run(cmd.split(),input=test_input2,encoding='utf-8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)  #プログラムを実行、出力及びエラーメッセージを取得
            #     #             except:
            #     #                 pass
            #     #             Outc2 = "予期せぬエラーが起きたようです。" #プログラム実行エラーとか，ctrl-cとか   
            #     #             if c2.returncode == 1:  #プログラム異常終了
            #     #                 Outc2 = c2.stderr  #エラー内容
            #     #             elif c2.returncode == 0:  #プログラム正常終了
            #     #                 Outc2 = c2.stdout  #標準出力
            #     #                 if test_output2 == Outc2:
            #     #                     test2 = "test2OK"
            #     #                 else:
            #     #                     test2 = "test2NOT!!!!!" 
            #     #             print(test2)
            #     #             print(Outc2)
            #     #             # time.sleep(2)
                            
            #     #             # old = 1.0#テスト用　後で直して

            #     #             #test_inputが両方ある場合にのみ対応，片方だけにも対応するものは後で作る
            #     #             if test1 == "test1OK" and test2 == "test2OK":
            #     #                 # ６つの類似度の平均でやりたかったけどエラーになる
            #     #                 # keisann = old + jaro + dice + simpson + ted + to
            #     #                 # print(round(keisann,3))
            #     #                 if old > 0.8:
            #     #                     testcheck_flag = 2
            #     #                     print("dekitayooooooo")

            #     #     else: #未テスト,あとでテストする
            #     #         # if testOutr1 == Out:
            #     #         #     test3 = "test3OK"
            #     #         #     testcheck_flag = 2
            #     #         #     if old > 0.8:
            #     #         #         testcheck_flag = 2
            #     #         #         print("dekitayooooooo3")
            #     #         if old == 1.0: #標準入力がない場合は，oldが１だったら正解しているものとする．
            #     #             testcheck_flag = 2
            #     #             print("dekitayooooooo3")                        

            #     # if testcheck_flag ==2:
            #     #     error_flag = 2 #フラグを達成済みを示す2にするため
            #     #     last_time = history_list[-1][3]
            #     #     if status: #既にstudent_idとtask_idのstatusが保存されているなら，レコード編集
            #     #         a = (error_flag, last_time, i[0],n[0])
            #     #         c.execute("update status SET status_flag=?, judge_time=? where  student_id=? and task_id=?", a)
            #     #         conn.commit()
            #     #     else: #まだstudent_idとtask_idのstatusが保存されていなければ，新規レコード
            #     #         a = (i[0],n[0], error_flag, 0, last_time)
            #     #         c.execute("insert into status (student_id,task_id,status_flag,guid_flag,judge_time) values(?,?,?,?,?)", a)
            #     #         conn.commit()    
            #     # #ここまでコメントアウト

            #     # else: 
            #     #ここまで変更点




                #     last_time = history_list[-1][3]
                #     # 直近三回ともコンパイルエラー無しなら-1,そうでなければ0
                #     if history_list[-1][4] == 1 & history_list[-2][4] == 1 & history_list[-3][4] == 1:
                #         error_flag = -1
                #     else:
                #         error_flag = 0

                #     if status: #既にstudent_idとtask_idのstatusが保存されているなら，レコード編集
                #         a = (error_flag, last_time, i[0],n[0])
                #         c.execute("update status SET status_flag=?, judge_time=? where  student_id=? and task_id=?", a)
                #         conn.commit()
                #     else: #まだstudent_idとtask_idのstatusが保存されていなければ，新規レコード
                #         a = (i[0],n[0], error_flag, 0, last_time)
                #         c.execute("insert into status (student_id,task_id,status_flag,guid_flag,judge_time) values(?,?,?,?,?)", a)
                #         conn.commit()
                # else:   #history_listの要素数が1以上3未満なら
                #     last_time = history_list[-1][3]
                #     error_flag = 0
                #     if status: #既にstudent_idとtask_idのstatusが保存されているなら，レコード編集
                #         a = (error_flag, last_time, i[0],n[0])
                #         c.execute("update status SET status_flag=?, judge_time=? where  student_id=? and task_id=?", a)
                #         conn.commit()
                #     else: #まだstudent_idとtask_idのstatusが保存されていなければ，新規レコード
                #         a = (i[0],n[0], error_flag, 0, last_time)
                #         c.execute("insert into status (student_id,task_id,status_flag,guid_flag,judge_time) values(?,?,?,?,?)", a)
                #         conn.commit()


judge()