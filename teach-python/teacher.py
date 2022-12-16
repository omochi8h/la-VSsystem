import sys,os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import *

import sqlite3
from pathlib import Path
import time
import linenumber
import datetime

kadaiidentify = 0 #課題識別用。0：取組中の課題，1～：データベースに入れた順
seitoidentify = "" #生徒識別用。
narabi = 0 #学習者リスト並び変え用
mushi = "1"
mush = 0 #mushが1ならmushi日以前のデータを無視

path = Path(__file__).parent   # 現在のディレクトリ
path /= '../'     # ディレクトリ移動
path_str = str(Path(path.resolve()))
sql_path = path_str + '/assist.sqlite3'

conn = sqlite3.connect(sql_path)
c = conn.cursor()


def judge():
    c.execute("select student_id from student")
    student_list = c.fetchall()
    c.execute("select task_id from task")
    task_list = c.fetchall()

    for i in student_list:
        for n in task_list:
            c.execute("select * from history where student_id=? and task_id=?", (i[0],n[0]))
            history_list = c.fetchall()
            if history_list: #history_listが空ではなければ
                last_time = history_list[-1][3]
                # 直近三回ともコンパイルエラーなら-1,そうでなければ0
                if history_list[-1][4] == -1 & history_list[-2][4] == -1 & history_list[-3][4] == -1:
                    error_flag = -1
                else:
                    error_flag = 0
                
                c.execute("select *from status where student_id=? and task_id=?", (i[0],n[0]))
                status = c.fetchone()
                if status: #既にstudent_idとtask_idのstatusが保存されているなら，レコード編集
                    a = (error_flag, last_time, i[0],n[0])
                    c.execute("update status SET status_flag=?, judge_time=? where  student_id=? and task_id=?", a)
                    conn.commit()
                else: #まだstudent_idとtask_idのstatusが保存されていなければ，新規レコード
                    a = (i[0],n[0], error_flag, 0, last_time)
                    c.execute("insert into status (student_id,task_id,status_flag,guid_flag,judge_time) values(?,?,?,?,?)", a)
                    conn.commit()

judge()
# sys.exit()


#表示する画面の制御(下の方に定義してあるmove関数も参照)
class MainWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        hbox = QHBoxLayout()

        # global menu
        # menu = Menu(self) #画面左側のメニュー
        # menu.setFrameShape(QFrame.Panel) #外枠(新しいプログラムで外枠がいらないならクラス定義でQFrameにする必要がない。teaher2.pyを参照)

        global studentlist
        studentlist = StudentList(self) #学生リスト
        studentlist.setFrameShape(QFrame.Panel)


        global manual
        manual = Manual(self) #マニュアル
        manual.setFrameShape(QFrame.Panel)

        # global kadaihozon
        # kadaihozon = KadaiHozon(self) #新規課題保存画面
        # kadaihozon.setFrameShape(QFrame.Panel)

        # global kadaidetail
        # kadaidetail = KadaiDetail(self) #課題情報画面
        # kadaidetail.setFrameShape(QFrame.Panel)

        # global seitodetail
        # seitodetail = SeitoDetail(self) #学習者情報画面
        # seitodetail.setFrameShape(QFrame.Panel)

        # hbox.addWidget(menu)
        hbox.addWidget(studentlist)
        hbox.addWidget(manual)
        # hbox.addWidget(kadaihozon)
        # hbox.addWidget(kadaidetail)
        # hbox.addWidget(seitodetail)

        # kadaihozon.hide() #一度隠す→move関数で表示を制御
        # kadaidetail.hide()
        # seitodetail.hide()

        self.setLayout(hbox)

class Menu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.check = QCheckBox(" ") #無視するか決める用
        if mush == 1:
            self.check.setChecked(True)
        self.check.clicked.connect(self.renew)


        kadailist = ["取り組み中の課題"] #kadailistに課題名を入れていく
        c.execute("select task_name from task")
        for kadai in c:
            kadailist.append(kadai["name"])
        self.combobox1.addItems(kadailist)
        self.combobox1.setCurrentIndex(kadaiidentify)
        self.combobox1.currentIndexChanged.connect(self.kadaisentaku)

        self.combobox2 = QComboBox() #並び順リストボックス
        font = QFont()
        font.setPointSize(17)
        self.combobox2.setFont(font)
        self.combobox2.setStyleSheet("background-color:white")
        sortlist = ["名前順","課題名順","状態順","躓き検出時刻が古い順"]
        self.combobox2.addItems(sortlist)
        self.combobox2.setCurrentIndex(narabi)
        self.combobox2.currentIndexChanged.connect(self.narabikae)




    def renew(self): #更新ボタン，無視チェックボックスのクリックで呼び出される
        global mush
        global mushi
        global seitoidentify
        if self.check.checkState(): #無視するかどうかチェックボックスで判断
            try:
                float(self.edit.text()) #バグ回避。数字のみで入力されたか判断
            except:
                message = QMessageBox()
                message.setWindowTitle("失敗")
                message.setText("数字のみで入力してください")
                okbutton = message.addButton("OK", QMessageBox.AcceptRole)
                message.setDefaultButton(okbutton)
                message.setFont(QtGui.QFont("MS　ゴシック", 16, QFont.Medium))
                m = message.exec_()
            else:
                mushi = self.edit.text()
                mush = 1
        else:
            mush = 0
            mushi = self.edit.text() #無視はしないがテキスト内容は保存しておく。(moveすると消えるから)
        
        if seitoidentify == "": #学習者詳細画面以外にいる場合
            move(0)
        else: #学習者詳細画面にいる場合
            move(3)

    def kadaihozon(self): #新規課題保存ボタンで呼び出される
        move(1)

    def kadaisentaku(self): #課題リストボックスの変更で呼び出される
        global kadaiidentify
        kadaiidentify = self.combobox1.currentIndex()
        if kadaiidentify == 0: #0(取組中の課題)で課題情報画面行くとバグる
            move(0)
        else:
            move(2)

    def narabikae(self): #並び変えリストボックスの変更で呼び出される
        global narabi
        narabi = self.combobox2.currentIndex()
        move(0)

    def syuuryou(self): #終了ボタンで呼び出される
        message = QMessageBox()
        message.setWindowTitle("確認")
        message.setText("終了しますか？")
        yesbutton = message.addButton("   はい   ", QMessageBox.ActionRole)
        nobutton = message.addButton("   いいえ   ", QMessageBox.ActionRole)
        message.setFont(QtGui.QFont("MS　ゴシック",16, QFont.Medium))
        m = message.exec_()

        if message.clickedButton() == yesbutton:
            QCoreApplication.instance().quit()
        elif message.clickedButton() == nobutton:
            pass


class StudentList(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        l = QLabel("学生リスト",self)
        font = QFont()
        font.setPointSize(17)
        l.setFont(font)
        l.move(265,10)

        button1 = QPushButton("更新", self)
        button1.setFont(QtGui.QFont("MS　ゴシック", 20, QFont.Medium))
        button1.setStyleSheet("background-color:Gainsboro")
        # button1.clicked.connect(self.renew)

        button2 = QPushButton("新規課題保存", self)
        button2.setFont(QtGui.QFont("MS　ゴシック", 20, QFont.Medium))
        # button2.setStyleSheet("background-color:Gainsboro")
        # button2.clicked.connect(self.kadaihozon)

        button3 = QPushButton("終了", self)
        button3.setFont(QtGui.QFont("MS　ゴシック", 20, QFont.Medium))
        button3.setStyleSheet("background-color:Gainsboro")
        # button3.clicked.connect(self.syuuryou)

        # label1 = QLabel('課題を選択してください')
        # font = QFont()
        # font.setPointSize(17)
        # label1.setFont(font)

        label2 = QLabel('学習者リスト')
        font = QFont()
        font.setPointSize(17)
        label2.setFont(font)

        self.edit = QLineEdit(self) #過去のデータを無視する日数を指定する用
        self.edit.setStyleSheet('background-color: white')
        font = self.edit.font()  
        font.setPointSize(20)
        self.edit.setFont(font)
        self.edit.setTextMargins(0,0,0,0)
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Minimum)
        self.edit.setText(mushi)

        # self.combobox2 = QComboBox() #並び順リストボックス
        # font = QFont()
        # font.setPointSize(17)
        # self.combobox2.setFont(font)
        # self.combobox2.setStyleSheet("background-color:white")
        # sortlist = ["名前順","課題名順","状態順","躓き検出時刻が古い順"]
        # self.combobox2.addItems(sortlist)
        # self.combobox2.setCurrentIndex(narabi)
        # self.combobox2.currentIndexChanged.connect(self.narabikae)

        label3 = QLabel('日以上前のデータを無視')
        font = QFont()
        font.setPointSize(17)
        label3.setFont(font)

        label4 = QLabel(' ') #レイアウト用の空白ラベル
        font = QFont()
        font.setPointSize(17)
        label4.setFont(font)

        space = QSpacerItem(100,40,QSizePolicy.Maximum,QSizePolicy.Maximum) #レイアウト用の空白

        self.combobox1 = QComboBox() #課題リストボックス
        font = QFont()
        font.setPointSize(17)
        self.combobox1.setFont(font)
        self.combobox1.setStyleSheet("background-color:white")

        table = ScrollTable(self) #学習者の表。別クラスで定義
        h1 = QHBoxLayout()
        v1 = QVBoxLayout()
        h2 = QHBoxLayout()
        h3 = QHBoxLayout()
        h2.addWidget(label4)
        h2.addWidget(label4)
        h2.addWidget(label4)
        for i in range(3):
            h3.addWidget(label4)
        # h3.addWidget(self.check)
        h2.addLayout(h3)
        h2.addWidget(self.edit)
        h2.addWidget(label3)
        h1.addWidget(button1)
        h1.addWidget(button2)
        h1.addWidget(button3)
        v1.addSpacerItem(space)
        # v1.addWidget(label1)
        v1.addWidget(self.combobox1)
        v1.addSpacerItem(space)
        v1.addWidget(label2)
        # v1.addWidget(self.combobox2)
        v1.addLayout(h2)
        v1.addWidget(table)
        v1.addSpacerItem(space)
        v1.addLayout(h1)
        self.setLayout(v1)


class ScrollTable(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        vbox = QVBoxLayout()
        student_set = set() #学習者のセット(被りなし)
        data = [] #表のデータを格納。rowも参照
        

        c.execute("select *from status")
        status_list = c.fetchall()

        for status in status_list:
            row = [0,0,0,0,0]
            row[0] = status[1]
            row[1] = status[2]
            row[2] = status[3]
            row[3] = status[5]
            row[4] = 0
            data.append(row)
        

        # for i in range(len(status_list)): #i行
        #     # for j in range(len(data[i])): #j列
        #     self.table.setItem(i,0,QTableWidgetItem(status_list[i][1]))
        #     self.table.setItem(i,1,QTableWidgetItem(status_list[i][2]))
        #     self.table.setItem(i,2,QTableWidgetItem(status_list[i][3]))
        #     self.table.setItem(i,3,QTableWidgetItem(status_list[i][5]))
        #     self.table.setItem(i,4,QTableWidgetItem(status_list[i][4])) #実際に表にデータを入れる

        self.table = QTableWidget(len(data),5) #表を宣言
        self.table.setStyleSheet("background-color: White")
        self.table.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.MinimumExpanding)
        self.table.setFont(QtGui.QFont("MS　ゴシック", 15, QFont.Medium))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header = ["学習者名","課題名","状態","躓き検出時刻",""]
        self.table.setHorizontalHeaderLabels(header)
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)

        #narabiの値によってdataを並び変える
        if narabi == 1:
            data = sorted(data,key=lambda x:x[1])
        elif narabi == 2:
            data = sorted(data,key=lambda x:x[2])
        elif narabi == 3:
            data = sorted(data,key=lambda x:x[5],reverse=True)

        for d in data:
            c.execute("select student_number from student where student_id=?", (str(d[0])))   
            student_number = c.fetchone()
            print(student_number) 
            d[0] = " " + str(student_number[0]) + " "
            c.execute("select task_name from task where task_id=?", (str(d[1])))   
            task_name = c.fetchone()
            print(task_name) 
            d[1] = " " + str(task_name[0]) + " "
            if d[2] == -1:
                d[2] = "躓き"
            else:
                d[2] = "躓いてない"   
            
        print(datetime.datetime.now())


        for i in range(len(data)): #i行
            for j in range(len(data[i])): #j列
                self.table.setItem(i,j,QTableWidgetItem(data[i][j])) #実際に表にデータを入れる
            
            # #色変え
            # if " 達成 " in data[i][2]:
            #     self.table.item(i,2).setForeground(QColor(255,0,0))
            # if " コンパイルなし " in data[i][2]:
            #     self.table.item(i,2).setBackground(QColor(200,200,200))
            # if " 躓き発生 " in data[i][2]:
            #     self.table.item(i,2).setBackground(QColor(255,80,80))
            # if " 文法エラー " in data[i][2]:
            #     self.table.item(i,2).setBackground(QColor(117,172,255))

            # for j in range(len(data[i])):
            #     self.table.item(i,j).setTextAlignment(Qt.AlignCenter) #文字を中央揃え

            button = QPushButton("詳細")
            button.setFont(QtGui.QFont("MS　ゴシック", 15, QFont.Medium))
            button.setStyleSheet("background-color:whitesmoke")
            # button.index = data[i][0].replace(" ","") #それぞれのボタンのメンバ変数としてdata[i][0](学習者名)を設定
            # button.clicked.connect(self.seitodetail)
            # if seitoidentify == button.index: #学習者詳細画面にいるならボタンの色を変えて分かりやすくする
            #     button.setStyleSheet("background-color:mediumspringgreen")
            self.table.setCellWidget(1,4,button) #実際に表にボタンを入れる
        vbox.addWidget(self.table)
        self.setLayout(vbox)

        
    


class Manual(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        l = QLabel("マニュアル",self)
        font = QFont()
        font.setPointSize(17)
        l.setFont(font)
        l.move(265,10)

        label1 = QLabel("課題を選ぶと詳細が表示されます。\n課題の編集・削除が可能です。")
        font = QFont()
        font.setPointSize(15)
        label1.setFont(font)

        label2 = QLabel("学習者リストを指定の方法で並び変えることができます。\n\nテキストボックスに実数を入力してチェックを入れると\n指定した日数以前のデータが表示されなくなります。")
        font = QFont()
        font.setPointSize(15)
        label2.setFont(font)

        label3 = QLabel("状態")
        font = QFont()
        font.setPointSize(15)
        label3.setFont(font)

        label4 = QLabel("：ロジック構成面の躓きが発生したと推測されます")
        font = QFont()
        font.setPointSize(15)
        label4.setFont(font)

        label5 = QLabel()
        image = QImage("tsumaduki.png")
        label5.setPixmap(QPixmap.fromImage(image))

        label6 = QLabel("：文法的に躓いている可能性があります")
        font = QFont()
        font.setPointSize(15)
        label6.setFont(font)

        label7 = QLabel()
        image = QImage("bunpouerror.png")
        label7.setPixmap(QPixmap.fromImage(image))

        label8 = QLabel("：まだ一度もコンパイルがされていない状態です")
        font = QFont()
        font.setPointSize(15)
        label8.setFont(font)

        label9 = QLabel()
        image = QImage("compilenashi.png")
        label9.setPixmap(QPixmap.fromImage(image))

        label10 = QLabel("：学習者により課題が達成とされています")
        font = QFont()
        font.setPointSize(15)
        label10.setFont(font)

        label11 = QLabel()
        image = QImage("tassei.png")
        label11.setPixmap(QPixmap.fromImage(image))

        label12 = QLabel("：上記以外の学生です")
        font = QFont()
        font.setPointSize(15)
        label12.setFont(font)

        label13 = QLabel()
        image = QImage("torikumityu.png")
        label13.setPixmap(QPixmap.fromImage(image))

        label15 = QLabel("更新：画面を更新\n新規課題保存：新しい課題をデータベースに保存\n終了：アプリを終了")
        font = QFont()
        font.setPointSize(15)
        label15.setFont(font)

        label16 = QLabel()
        image = QImage("shousai.png")
        label16.setPixmap(QPixmap.fromImage(image))

        label17 = QLabel("を押すと学習者の詳細な状況を閲覧できます。")
        font = QFont()
        font.setPointSize(15)
        label17.setFont(font)

        label22 = QLabel()
        image = QImage("shidouzumi.png")
        label22.setPixmap(QPixmap.fromImage(image))

        label23 = QLabel("を押すと参照中の学習者の躓き情報をリセットできます。")
        font = QFont()
        font.setPointSize(15)
        label23.setFont(font)

        label24 = QLabel()
        image = QImage("gakusyusyasakujo.png")
        label24.setPixmap(QPixmap.fromImage(image))

        label25 = QLabel("を押すと参照中の学習者情報を削除できます。")
        font = QFont()
        font.setPointSize(15)
        label25.setFont(font)

        v = QVBoxLayout()
        g1 = QGridLayout()
        g2 = QGridLayout()
        space = QSpacerItem(100,60,QSizePolicy.Maximum,QSizePolicy.Maximum)
        v.addSpacerItem(space)
        v.addWidget(label1)
        v.addSpacerItem(space)
        v.addWidget(label2)
        v.addStretch(1)
        v.addWidget(label3)
        g1.addWidget(label5,0,0,1,1)
        g1.addWidget(label4,0,1,1,4)
        g1.addWidget(label7,1,0,1,1)
        g1.addWidget(label6,1,1,1,4)
        g1.addWidget(label9,2,0,1,1)
        g1.addWidget(label8,2,1,1,4)
        g1.addWidget(label11,3,0,1,1)
        g1.addWidget(label10,3,1,1,4)
        g1.addWidget(label13,4,0,1,1)
        g1.addWidget(label12,4,1,1,4)
        v.addLayout(g1)
        v.addStretch(1)
        v.addStretch(1)
        g2.addWidget(label16,0,0,1,1)
        g2.addWidget(label17,0,1,1,6)
        g2.addWidget(label22,1,0,1,1)
        g2.addWidget(label23,1,1,1,6)
        g2.addWidget(label24,2,0,1,1)
        g2.addWidget(label25,2,1,1,6)
        v.addLayout(g2)
        v.addStretch(1)
        v.addWidget(label15)
        self.setLayout(v)

# class KadaiHozon(QFrame):
#     def __init__(self, parent=None):
#         super().__init__(parent)

# class KadaiDetail(QFrame):
#     def __init__(self, parent=None):
#         super().__init__(parent)

# class SeitoDetail(QFrame):
#     def __init__(self, parent=None):
#         super().__init__(parent)


class App(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("教員用")
        global tab
        tab = MainWindow(self)
        self.addTab(tab, "MainWindow")
        
        self.setStyleSheet("QTabWidget::pane { border: 0; }")
        self.tabBar().hide()
        self.resize(1260, 900)
        self.move(10,20)
        self.setStyleSheet('background-color:AliceBlue')

#画面の表示切り替えをする関数
def move(page): #page引数によって表示する画面を決定
    global seitoidentify
    if page != 3:
        seitoidentify = "" #seitodetailにいない間は""にする。詳細ボタンの色，更新ボタンの移動先を制御するため

    #一度タブを消して再度タブを作る→こうしないと変数が更新されない
    window.removeTab(0)
    tab = MainWindow(window)
    window.addTab(tab,"MainWindow")
    window.setCurrentIndex(0)

    # manual.hide() #一度全部隠す
    # kadaihozon.hide()
    # kadaidetail.hide()
    # seitodetail.hide()

    # if page == 0: #pageの値によって画面を表示
    #     manual.show()
    # elif page == 1:
    #     kadaihozon.show()
    # elif page == 2:
    #     kadaidetail.show()
    # elif page == 3:
    #     seitodetail.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    global window
    window = App()
    window.show()
    app.exec_()