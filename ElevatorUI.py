from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QLabel,QWidget,QVBoxLayout,QPushButton,QMenu,QMenuBar,QAction,qApp
from PyQt5.QtCore import Qt,QRect,QPropertyAnimation
from PyQt5.QtGui import QPixmap,QPalette,QFont,QIcon,QPen,QPainter


class UiMainWindow(object):
    def setUI(self, MainWindow):
        # 主窗口处理

        MainWindow.setObjectName("Elevator")  #窗口名称
        MainWindow.setFixedSize(820, 680)     #窗口大小 设置为固定大小

        MainWindow.setStyleSheet("#Elevator{border-image:url(res/background.png)}")  #设置背景图片
        self.Widget = QWidget(MainWindow)
        self.Widget.setFixedSize(820, 680)
        self.Widget.setWindowTitle("Elevator Simulator")   #设置标题

        #创建菜单栏
        menubar = MainWindow.menuBar()
        menubar.setNativeMenuBar(False)
        menuStart = menubar.addMenu('&开始')
        menuQuit = menuStart.addMenu('&退出')
        exitAct = QAction(MainWindow)
        exitAct.setShortcut('ctrl+q')
        exitAct.triggered.connect(qApp.quit)
        menuQuit.addAction(exitAct)


        #上下按钮图片导入 三种状态
        self.upBtnStyle = "QPushButton{border-image: url(res/up_hover.png)}"\
            "QPushButton:hover{border-image: url(res/up.png)}"\
            "QPushButton:pressed{border-image: url(res/up_pressed.png)}"
        self.downBtnStyle = "QPushButton{border-image: url(res/down_hover.png)}" \
            "QPushButton:hover{border-image: url(res/down.png)}" \
            "QPushButton:pressed{border-image: url(res/down_pressed.png)}"

        #设置电梯图片
        self.elevatorPix = {}
        for i in range(1, 6):
            self.elevatorPix[i] = QLabel(MainWindow) #标签类
            self.elevatorPix[i].setPixmap(QPixmap("res/elevator.png")) #设置图片
            self.elevatorPix[i].setGeometry(QRect(230+130*(i-1),630, 35, 35)) #设置位置与大小
            self.elevatorPix[i].setScaledContents(True)

        self.locLabel = {}
        for i in range(1, 6):
            self.locLabel[i] = QLabel(MainWindow)
            self.locLabel[i].setText("当前楼层: 1")    # 文字内容 显示所在楼层
            self.locLabel[i].setGeometry(QRect(170+130*(i-1), 30, 100, 30)) #文字大小与位置
            font = QFont()
            font.setPointSize(15)   #字体大小
            font.setStyleStrategy(QFont.PreferAntialias)
            self.locLabel[i].setFont(font)
            self.locLabel[i].setStyleSheet("color: rgb(70, 130, 180);")
            self.locLabel[i].setTextFormat(Qt.AutoText)
            self.locLabel[i].setWordWrap(True)

        #初始化动画内容
        self.elevatorAnim = {}
        for i in range(1, 6):
            self.elevatorAnim[i] = QPropertyAnimation(self.elevatorPix[i], b"geometry")

        #创建标签 写明楼层与上下
        layerFont = QFont()
        layerFont.setPointSize(15)
        self.layer = QLabel(MainWindow)
        self.layer.setText("楼层")
        self.layer.setGeometry(15,25,45,35)
        self.layer.setFont(layerFont)
        self.layer.setStyleSheet("color:rgb(0,0,0);")

        self.upLabel = QLabel(MainWindow)
        self.upLabel.setText("上")
        self.upLabel.setFont(layerFont)
        self.upLabel.setGeometry(70,25,35,35)
        self.upLabel.setStyleSheet("color:rgb(0,0,0);")

        self.downLabel = QLabel(MainWindow)
        self.downLabel.setText("下")
        self.downLabel.setFont(layerFont)
        self.downLabel.setGeometry(113,25,35,35)
        self.downLabel.setStyleSheet("color:rgb(0,0,0);")

        #创建楼层号码标签
        NumFont = QFont()
        NumFont.setPointSize(15)
        for i in range(1,21):
            self.flr = QLabel(MainWindow)
            self.flr.setFont(NumFont)
            self.num = '第{}层'.format(i)
            self.flr.setText(self.num)
            self.flr.setGeometry(10,665 - i*30,50,35)
            self.flr.setStyleSheet("color:rgb(70, 130, 180);")
            self.flr.setAlignment(Qt.AlignCenter)



        # 创建向上向下的按钮（相当于每层楼道里的按钮） 20层 第一层没有向下 第20层没有向上
        self.upBtn = {}
        for i in range(1, 20):
            self.upBtn[i] = QPushButton(MainWindow)
            self.upBtn[i].setGeometry(QRect(70, 670 - i * 30, 25, 25))
            self.upBtn[i].setStyleSheet(self.upBtnStyle)

        self.downBtn = {}
        for i in range(2, 21):
            self.downBtn[i] = QPushButton(MainWindow)
            self.downBtn[i].setGeometry(QRect(110, 670 - i * 30, 25, 25))
            self.downBtn[i].setStyleSheet(self.downBtnStyle)

        #每部电梯内的楼层
        self.numBtn = [[]for i in range(6)]  # 为使索引序号与电梯序号对应起来，创建六个子数组，第0个不加操作
        for i in range(1, 6):
            self.numBtn[i].append(0)  # 为使索引序号与电梯楼层对应起来，在第0个位置添加空项，用0替代
            for j in range(1, 21):
                self.numBtn[i].append(QPushButton(MainWindow))
                self.numBtn[i][j].setGeometry(QRect(170+130*(i-1), 670 - j * 30, 25, 25))
                self.numBtn[i][j].setStyleSheet(
                    "QPushButton{border-image: url(res/"+str(j)+"_hover.png)}"
                    "QPushButton:hover{border-image: url(res/"+str(j)+".png)}"
                    "QPushButton:pressed{border-image: url(res/"+str(j)+"_pressed.png)}"
                    )







def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "anim"))

