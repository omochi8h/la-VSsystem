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
    json_path = path_str + '/data.json'
    answer_path = path_str + '/task-program/answer.c'
    answerexe_path = path_str + '/task-program/answer.exe'
    answercmd_path = path_str + '/task-program/answer'
    input_path = path_str + '/task-program/input.c'
    inputexe_path = path_str + '/task-program/input.exe'
    inputcmd_path = path_str + '/task-program/input'

    with open(json_path, 'r', encoding="utf-8") as f:
        data = json.load(f)
    
    conn = sqlite3.connect(sql_path)
    c = conn.cursor()

    # taskテーブル内にdata["task"]が無ければ，強制終了．あればid取得
    c.execute("select task_id from task where task_name = ?;", (data["task"],))
    list1 = c.fetchall()
    if len(list1) == 0:
        print('not task')
        quit()
    else:
        task_id = list1[0][0]
        print(task_id)

    # taskテーブル内にdata["student_number"]が無ければ，studentテーブルに新規登録.あればid取得
    c.execute("select student_id from student where student_number = ?;", (data["student_number"],))
    list2 = c.fetchall()
    if len(list2) == 0:
        print('not number')
        c.execute("insert into student (student_number,student_name) values(?,?)",(data["student_number"],data["student_name"],))
        conn.commit()
    else:
        student_id = list2[0][0]
        print(student_id)
    
    c.execute("select true_code,test_flag,test_input1,test_input2 from task where task_name = ?;", (data["task"],))
    test_data = c.fetchone()
    conn.close()
    test_flag = test_data[1]
    test_input1 = test_data[2]
    test_input2 = test_data[3]

    file = open(answer_path, 'w', encoding='utf-8')
    file.write(test_data[0])
    file.close()

    #input.cにあたるソースコードのコメント文を消す
    text1 = data["text"]
    while text1.count("//")>0:
        for i in range(text1.find("//"),len(text1)):
            if text1[i]=="\n":
                text1 = text1[:text1.find("//")] + text1[i+1:]
                break
            elif i == len(text1)-1:
                text1 = text1[:text1.find("//")]
    while text1.count("/*")>0 and text1.count("*/")>0:
        text1 = text1[:text1.find("/*")] + text1[text1.find("*/")+2:]
    #空白，改行を消す
    text1 = text1.replace(' ','')
    text1 = text1.replace('\r\n','')

    #正解ソースコードの加工 
    f = open(answer_path, 'r', encoding='utf-8')
    text2 = f.read()
    f.close()
    while text2.count("//")>0:
        for i in range(text2.find("//"),len(text2)):
            if text2[i]=="\n":
                text2 = text2[:text2.find("//")] + text2[i+1:]
                break
            elif i == len(text2)-1:
                text2 = text2[:text2.find("//")]
    while text2.count("/*")>0 and text2.count("*/")>0:
        text2 = text2[:text2.find("/*")] + text2[text2.find("*/")+2:]
    text2 = text2.replace(' ','')
    text2 = text2.replace('\n','')
 
    #類似度
    #OLD
    import Levenshtein

    a = len(text1)
    b = len(text2)
    d = Levenshtein.distance(text1,text2)

    if a > b:
        old = round((1-(d/a)),3)
    else:
        old = round((1-(d/b)),3)

    #Jaro
    d = Levenshtein.jaro(text1,text2)
    jaro = round(d,3)

    #Dice
    from pysummarization.similarity_filter import SimilarityFilter

    class Dice(SimilarityFilter):
        def calculate(self, str1, str2):
            x, y = self.unique(str1, str2)
            try:
                for i in map(len, (x, y)):
                    print(i)
                result = 2 * len(x & y) / float(sum(map(len, (x, y))))
            except ZeroDivisionError:
                result = 0.0
            return result

    dice = Dice()
    d = dice.calculate(text1,text2)
    dc = round(d,3)

    # Simpson
    class Simpson(SimilarityFilter):
        def calculate(self, str1, str2):
            x, y = self.unique(str1, str2)
            try:
                result = len(x & y) / float(min(map(len, (x, y))))
            except ZeroDivisionError:
                result = 0.0
            return result

    simpson = Simpson()
    d = simpson.calculate(text1,text2)
    sc = round(d,3)

    #TED，TO
    try:
        tree = treesimi2.func()
    except: #例外処理
        tree = [0,0]
    ted = tree[0]
    to = tree[1]

    print("old：" + str(old))
    print("jaro：" + str(jaro))
    print("dice：" + str(dc))
    print("simpson：" + str(sc))
    print("ted：" + str(ted))
    print("to：" + str(to))

    #プロンプト操作
    # e = self.err[-1]
    # cmd = ("clang -o input.exe input.c")
    # print(cmd)

    cmd = "clang -o " + inputexe_path + " " + input_path
    print(cmd)
     #コンパイルを実行、エラーメッセージを取得．標準入力が必要なら，第二引数にinput=inpを設定
    r1 = subprocess.run(cmd.split(),encoding='utf-8',stderr=subprocess.PIPE) 
    
    if r1.returncode == 1:  #コンパイル失敗
        error_flag = -1
        Out = r1.stderr  #エラー内容
    elif r1.returncode == 0:  #コンパイル成功
        cmd = inputcmd_path
        error_flag = 1
        try:
            r2 = subprocess.run(cmd.split(),encoding='utf-8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)  #プログラムを実行、出力及びエラーメッセージを取得
        except:
            pass
        Out = "予期せぬエラーが起きたようです。" #プログラム実行エラーとか，ctrl-cとか

        if r2.returncode == 1:  #プログラム異常終了
            Out = r2.stderr  #エラー内容
        elif r2.returncode == 0:  #プログラム正常終了
            Out = r2.stdout  #標準出力
    
    # fistoryテーブルにレコード挿入
    conn = sqlite3.connect(sql_path)
    c = conn.cursor()
    a = (student_id, task_id, data["time"], error_flag, data["text"], Out,old,jaro,dc,sc,ted,to)
    c.execute("insert into history (student_id,task_id,time,error_flag,answer_code,output,sim_old,sim_jaro,sim_dc,sim_sc,sim_ted,sim_to) values(?,?,?,?,?,?,?,?,?,?,?,?)", a)
    conn.commit()
    conn.close()

