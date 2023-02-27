import sys,json,pickle
import sqlite3
import os
from pathlib import Path

# student2.pyから引用
import time
# import linenumber
import subprocess
import treesimi2

if __name__ == "__main__":
    path = Path(__file__).parent   # 現在のディレクトリ
    path /= '../'     # ディレクトリ移動
    path_str = str(Path(path.resolve()))
    # sql_path = path_str + '/assist.sqlite3'
    # sql_path = path_str + '/test3.sqlite3'
    # sql_path = path_str + '/expt.sqlite3'
    sql_path = path_str + '/expt0218.sqlite3'
    # json_path = path_str + '/data.json'
    # answer_path = path_str + '/task-program/answer.c'
    # answerexe_path = path_str + '/task-program/answer.exe'
    # answercmd_path = path_str + '/task-program/answer'
    # input_path = path_str + '/task-program/input.c'
    # inputexe_path = path_str + '/task-program/input.exe'
    # inputcmd_path = path_str + '/task-program/input'
    expt_path = path_str + '/task-program/expt.c'
    exptexe_path = path_str + '/task-program/expt.exe'
    exptcmd_path = path_str + '/task-program/expt'
    expt1_path = 'C:/Users/stude/Desktop/211910023_iwase/expt1.c'
    expt1exe_path = 'C:/Users/stude/Desktop/211910023_iwase/expt1.exe'
    expt1cmd_path = 'C:/Users/stude/Desktop/211910023_iwase/expt1'
    
    conn = sqlite3.connect(sql_path)
    c = conn.cursor()

    c.execute("select history_id,error_flag,answer_code,output from history where output like '%Permission denied%'")
    list1=c.fetchall()
    # print(list1[0][3])
    # print(len(list1))
    
    for l in list1:
        print(l)
        

        # file = open(expt1_path, 'w', encoding='utf-8')
        # file.write(l[2])
        # file.close()

        # # cmd = "clang -o " + expt1exe_path + " " + expt1_path
        # cmd = "clang -o expt1.exe expt1.c"
        # print(cmd)
        # #コンパイルを実行、エラーメッセージを取得．標準入力が必要なら，第二引数にinput=inpを設定
        # r1 = subprocess.run(cmd.split(),encoding='utf-8',stderr=subprocess.PIPE) 
        
        # if r1.returncode == 1:  #コンパイル失敗
        #     error_flag = -1
        #     Out = r1.stderr  #エラー内容
        #     print(Out)
        # elif r1.returncode == 0:  #コンパイル成功
        #     cmd = 'expt1'
        #     error_flag = 1
        #     Out =''
            # try:
            #     r2 = subprocess.run(cmd.split(),encoding='utf-8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)  #プログラムを実行、出力及びエラーメッセージを取得
            # except:
            #     pass
            # Out = "予期せぬエラーが起きたようです。" #プログラム実行エラーとか，ctrl-cとか

            # if r2.returncode == 1:  #プログラム異常終了
            #     Out = r2.stderr  #エラー内容
            # elif r2.returncode == 0:  #プログラム正常終了
            #     Out = r2.stdout  #標準出力
        

        # fistoryテーブルにレコード挿入
        # conn = sqlite3.connect(sql_path)
        # c = conn.cursor()
        # a = (error_flag, Out, l[0])
        # print(error_flag)
        # c.execute("update history  SET error_flag=?,output=? where history_id=?", a)
        # conn.commit()

        conn = sqlite3.connect(sql_path)
        c = conn.cursor()
        a = (1,l[0])
        c.execute("update history  SET error_flag=? where history_id=?", a)
        conn.commit()
        
    conn.close()

