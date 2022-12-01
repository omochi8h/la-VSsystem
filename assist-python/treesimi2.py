import subprocess, re
from zss import simple_distance, Node
from pathlib import Path


def buildtree(name):
    cmd = ("clang -cc1 -dump-tokens {}".format(name))
    r = subprocess.run(cmd.split(),encoding='utf-8',stderr=subprocess.PIPE)
    text = r.stderr
    list0 = text.split("\n")
    tokens = []
    for line in list0:
        i = 0
        token1 = ""
        token2 = ""
        for l in line:
            if i == 0:
                if re.search(" ", l) != None:
                    i = 1
                else:
                    token1 = token1 + l
            elif i == 1:
                i = 2
            elif i == 2:
                if re.search("'", l) != None:
                    break
                else:
                    token2 = token2 + l
        if token1 != token2:
            token2 = token2.replace('"','')
            token2 = token2.replace("'","")
            tokens.append(token2)
    #print(tokens)

    cmd = ("clang -cc1 -ast-dump {}".format(name))
    #r = subprocess.run(cmd.split(),encoding='utf-8')
    r = subprocess.run(cmd.split(),encoding='utf-8',stdout=subprocess.PIPE)
    text = r.stdout
    list1 = text.split("\n")
    list2 = ["root"]

    i = 0
    for line in list1:
        if i == 0:
            if re.search('FunctionDecl', line) != None:
                if re.search('extern', line) != None:
                    pass
                else:
                    list2.append(line)
                    i = 1
        elif i == 1:
            if re.search('extern', line) == None:
                list2.append(line)
            else:
                i = 0

    list3 = []
    dig = []
    for line in list2:
        line = line + " "
        if "NULL" in line:
            continue
        i = 0
        strings = []
        string = ""
        for index,a in enumerate(line):
            if i == 0:
                if re.search("[a-zA-Z]", a) != None:
                    string = string + a
                    dig.append(int(index/2))
                    i = 1
            elif i == 1:
                if a == " ":
                    strings.append(string)
                    string = ""
                elif (re.search("'", a) != None) or (re.search('"', a) != None):
                    i = 2
                else:
                    string = string + a
            elif i == 2:
                if (re.search("'", a) != None) or (re.search('"', a) != None):
                    i = 1
                else:
                    string = string + a
        for token in strings:
            if token in tokens:
                string = token
                break
            else:
                string = strings[0]
        string = string.replace("Stmt","")
        string = string.replace("Decl","変数")
        string = string.replace("ArraySubscriptExpr","配列")
        string = string.replace("MemberExpr","構造体")
        try:
            string = bytes.fromhex(string).decode("utf-8")
        except:
            pass
        list3.append(string) 

    list4 = []
    dig2 = []

    for index,line in enumerate(list3):
        if re.search('ImplicitCastExpr', line) != None:
            for i in range(index+1,len(dig)):
                if dig[i] > dig[index]:
                    dig[i] = dig[i] - 1
                else:
                    break
        elif re.search('Compound',line) != None:
            for i in range(index+1,len(dig)):
                if dig[i] > dig[index]:
                    dig[i] = dig[i] - 1
                else:
                    break
        elif re.search('InitListExpr',line) != None:
            for i in range(index+1,len(dig)):
                if dig[i] > dig[index]:
                    dig[i] = dig[i] - 1
                else:
                    break
        elif re.search('CStyleCastExpr',line) != None:
            for i in range(index+1,len(dig)):
                if dig[i] > dig[index]:
                    dig[i] = dig[i] - 1
                else:
                    break
        elif re.search('CallExpr',line) != None:
            dig[index+2] = dig[index]
        else:
            list4.append(line)
            dig2.append(dig[index])

    bubungi = []
    def partial(index):
        part = [list4[index]]
        partson = []
        for i in range(index+1,len(dig2)):
            if dig2[i] == dig2[index]:
                break
            elif dig2[i] == dig2[index] + 1:
                partson.append(list4[i])
                partial(i)
        if len(partson) > 0:
            part.append(partson)
            bubungi.append(part)
    partial(0)

    dig2.append(1)
    tree = "(\n"
    defaulttree = "(\n"

    for index,node in enumerate(list4):
        tree = tree + "    " * dig2[index]
        defaulttree = defaulttree + "    " * dig2[index]
        if index != 0:
            tree = tree + ".addkid("
            defaulttree = defaulttree + ".addkid("
        tree = tree + "Node('{}')".format(node) + ")" * (dig2[index]-dig2[index+1]+1) + "\n"
        defaulttree = defaulttree + "Node('a')" + ")" * (dig2[index]-dig2[index+1]+1) + "\n"
    tree = tree + ")"
    defaulttree = defaulttree + ")"

    return tree,index+1,bubungi,defaulttree


def func():
    path = Path(__file__).parent   # 現在のディレクトリ
    # print(path)
    path /= '../'     # ディレクトリ移動
    path_str = str(Path(path.resolve()))
    input_path = path_str + '/task-program/input.c'
    answer_path = path_str + '/task-program/answer.c'

    a = buildtree(input_path)
    b = buildtree(answer_path)
    exec("A = {}".format(a[0]),globals())
    exec("B = {}".format(b[0]),globals())
    exec("A1 = {}".format(a[3]),globals())
    exec("B1 = {}".format(b[3]),globals())
    ted0 = simple_distance(A,B)
    ted1 = simple_distance(A1,B1)
    #ted0を木の編集距離の取りうる最大値で割りたい
    #A→Bにするときの最大値は，AとBの構造で一致する部分を「置換」，Aの構造のうちBと一致しない部分を「削除」，Bの構造のうちAと一致しない部分を「挿入」
    #A,Bと構造が全く同じ木defaulttreeを作って，その間の編集距離を求める(ted1)→これが上の「削除」と「挿入」としていることが一緒
    #a[1]+b[1]-ted1→これが上の「置換」の回数の2倍
    #よって編集距離の最大値は(a[1]+b[1]+ted1)/2
    ted = round(1-(ted0*2/(a[1]+b[1]+ted1)),3)
    #print("解答ソースコード構文木：\n" + str(a[0]))
    #print("解答ソースコード構文木の要素数：" + str(a[1]))
    #print("解答ソースコード構文木の部分木集合：\n" + str(a[2]))
    #print("正解ソースコード構文木：\n" + str(b[0]))
    #print("正解ソースコード構文木の要素数：" + str(b[1]))
    #print("正解ソースコード構文木の部分木集合：\n" + str(b[2]))
    #print("構文木間の編集距離：" + str(ted0))
    #print("TED類似度：" + str(ted))
    to0 = 0
    lena = len(a[2])
    lenb = len(b[2])
    for part in a[2]:
        if part in b[2]:
            b[2].remove(part)
            to0 = to0 + 1
    to = round(1-((lena-to0)+(lenb-to0))/(lena+lenb),3)
    #print("部分木集合間の一致個数：" + str(to0))
    #print("TO類似度：" + str(to))
    return ted, to

#func()