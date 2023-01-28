import sys,json,pickle
import sqlite3
import os
from pathlib import Path

# student2.py??????p
import time
# import linenumber
import subprocess
import treesimi2

if __name__ == "__main__":
    path = Path(__file__).parent   # ?????f?B???N?g??
    path /= '../'     # ?f?B???N?g?????
    path_str = str(Path(path.resolve()))
    # sql_path = path_str + '/assist.sqlite3'
    sql_path = path_str + '/test1.sqlite3'
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

    # task?e?[?u??????data["task"]?????????C?????I???D?????id?ï
    c.execute("select task_id from task where task_name = ?;", (data["task"],))
    list1 = c.fetchall()
    if len(list1) == 0:
        print('not task')
        quit()
    else:
        task_id = list1[0][0]
        print(task_id)

    # task?e?[?u??????data["student_number"]?????????Cstudent?e?[?u????V?K?o?^.?????id?ï
    c.execute("select student_id from student where student_number = ?;", (data["student_number"],))
    list2 = c.fetchall()
    if len(list2) == 0:
        print('not number')
        c.execute("insert into student (student_number,student_name) values(?,?)",(data["student_number"],data["student_name"],))
        conn.commit()
    else:
        student_id = list2[0][0]
        print(student_id)
    
        #??????e?X?g?????????o
    c.execute("select true_code,test_flag,test_input1,test_input2 from task where task_name = ?;", (data["task"],))
    test_data = c.fetchone()
    conn.close()
    test_flag = test_data[1]
    test_input1 = test_data[2]
    test_input2 = test_data[3]

    file = open(answer_path, 'w', encoding='utf-8')
    file.write(test_data[0])
    file.close()

    #input.c???????\?[?X?R?[?h??R?????g????????
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
    #??C???s??????
    text1 = text1.replace(' ','')
    text1 = text1.replace('\r\n','')

    #?????\?[?X?R?[?h????H 
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
 
    #????x
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

    #TED?CTO
    try:
        tree = treesimi2.func()
    except: #??O????
        tree = [0,0]
    ted = tree[0]
    to = tree[1]

    print("old?F" + str(old))
    print("jaro?F" + str(jaro))
    print("dice?F" + str(dc))
    print("simpson?F" + str(sc))
    print("ted?F" + str(ted))
    print("to?F" + str(to))

    #?v?????v?g????
    # e = self.err[-1]
    # cmd = ("clang -o input.exe input.c")
    # print(cmd)

    #test??R???p?C?????????o
    cmd_test = "clang -o " + answerexe_path + " " + answer_path

    test = subprocess.run(cmd_test.split(),encoding='utf-8',stderr=subprocess.PIPE) 
    
    if test.returncode == 1:  #?R???p?C?????s
        testOut = test.stderr  #?G???[???e
        print(testOut)
    elif test.returncode == 0:  #?R???p?C??????
        cmd_test = inputcmd_path
        print("seikoudayo")
        try:
            if test_flag == '1': #test??W?????????R???p?C??
                if test_input1 != None:
                    test_c1 = subprocess.run(cmd_test.split(),input=test_input1,encoding='utf-8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                    if test_c1.returncode == 1:  #?v???O???????I??
                        testOutc1 = test_c1.stderr  #?G???[???e
                    elif test_c1.returncode == 0:  #?v???O????????I??
                        testOutc1 = test_c1.stdout  #?W???o??
                        print("testout1dayo")

                if test_input2 != None:
                    test_c2 = subprocess.run(cmd_test.split(),input=test_input2,encoding='utf-8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                    if test_c2.returncode == 1:  #?v???O???????I??
                        testOutc2 = test_c2.stderr  #?G???[???e
                    elif test_c2.returncode == 0:  #?v???O????????I??
                        testOutc2 = test_c2.stdout  #?W???o??
                        print("testout2dayo")
      
            else:#test??W?????????R???p?C??
                test_r1 = subprocess.run(cmd_test.split(),encoding='utf-8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                if test_r1.returncode == 1:  #?v???O???????I??
                    testOutr1 = test_r1.stderr  #?G???[???e
                elif test_r1.returncode == 0:  #?v???O????????I??
                    testOutr1 = test_r1.stdout  #?W???o??
                    print("testoutrrrrrr1dayo")

        except:
            pass
        # testOutc1 = "?\??????G???[???N??????????B" #?v???O???????s?G???[????Cctrl-c???
        # testOutc2 = "?\??????G???[???N??????????B"
        # testOutr1 = "?\??????G???[???N??????????B"

    cmd = "clang -o " + inputexe_path + " " + input_path
     #?R???p?C???????s?A?G???[???b?Z?[?W???ï?D?W????????K?v???C????????input=inp????
    r1 = subprocess.run(cmd.split(),encoding='utf-8',stderr=subprocess.PIPE) 
    
    if r1.returncode == 1:  #?R???p?C?????s
        error_flag = -1
        Out = r1.stderr  #?G???[???e
    elif r1.returncode == 0:  #?R???p?C??????
        cmd = inputcmd_path
        error_flag = 1
        try:
            r2 = subprocess.run(cmd.split(),encoding='utf-8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)  #?v???O?????????s?A?o??y?„…G???[???b?Z?[?W???ï
        except:
            pass
        Out = "?\??????G???[???N??????????B" #?v???O???????s?G???[????Cctrl-c???

        if r2.returncode == 1:  #?v???O???????I??
            Out = r2.stderr  #?G???[???e
        elif r2.returncode == 0:  #?v???O????????I??
            Out = r2.stdout  #?W???o??

        #?e?X?g??r?p?R???p?C??
        if test_flag == '1':
            if test_input1 != None:
                try:
                    c1 = subprocess.run(cmd.split(),input=test_input1,encoding='utf-8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)  #?v???O?????????s?A?o??y?„…G???[???b?Z?[?W???ï
                except:
                    pass
                Outc1 = "?\??????G???[???N??????????B" #?v???O???????s?G???[????Cctrl-c???
                if c1.returncode == 1:  #?v???O???????I??
                    Outc1 = c1.stderr  #?G???[???e
                elif c1.returncode == 0:  #?v???O????????I??
                    Outc1 = c1.stdout  #?W???o??
                    if testOutc1 == Outc1:
                        test1 = "test1OK"
                    else:
                        test1 = "test1NOT!!!!!"
                print(test1)

            if test_input2 != None:
                try:
                    c2 = subprocess.run(cmd.split(),input=test_input2,encoding='utf-8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)  #?v???O?????????s?A?o??y?„…G???[???b?Z?[?W???ï
                except:
                    pass
                Outc2 = "?\??????G???[???N??????????B" #?v???O???????s?G???[????Cctrl-c???   
                if c2.returncode == 1:  #?v???O???????I??
                    Outc2 = c2.stderr  #?G???[???e
                elif c2.returncode == 0:  #?v???O????????I??
                    Outc2 = c2.stdout  #?W???o??
                    if testOutc2 == Outc2:
                        test2 = "test2OK"
                    else:
                        test2 = "test2NOT!!!!!" 
                print(test2)

            #test_input??????????????????C?„E???????????????????????
            if test1 == "test1OK" and test2 == "test2OK":
                # ?U??????x??????????????????G???[????
                # keisann = old + jaro + dice + simpson + ted + to
                # print(round(keisann,3))
                if old > 0.8:
                    error_flag = 2
                    print("dekitayooooooo")

        else: #???e?X?g,?????e?X?g????
            if testOutr1 == Out:
                test3 = "test3OK"
                error_flag = 2
                if old > 0.8:
                    error_flag = 2
                    print("dekitayooooooo3")



    # print(Out)
        # if e == 0.5:  #?O???R???p?C?????G???[????
        #     Error = 1
        # else:  #?O???R???p?C?????G???[???
        #     Error = e * 1.5
    
    # fistory?e?[?u??????R?[?h?}??
    conn = sqlite3.connect(sql_path)
    c = conn.cursor()
    a = (student_id, task_id, data["time"], error_flag, data["text"], Out,old,jaro,dc,sc,ted,to)
    c.execute("insert into history (student_id,task_id,time,error_flag,answer_code,output,sim_old,sim_jaro,sim_dc,sim_sc,sim_ted,sim_to) values(?,?,?,?,?,?,?,?,?,?,?,?)", a)
    conn.commit()
    conn.close()

