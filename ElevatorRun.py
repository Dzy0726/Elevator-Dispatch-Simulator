import threading
import functools
import time
from PyQt5 import QtCore, QtGui
import sys


class Elevator():

    """
        创建一个电梯调度类
        goingUp标志着电梯正在向上，是一个集合
        goingDown标志着电梯正在向下，是一个集合
        lastTimeRise标志电梯上一次是上行的状态
        lastTimeDrop标志电梯上一次是下行的状态
        location是当前电梯在的楼层
        unprocessedUp中记录着某电梯将要进行但是还没有开始进行的上升请求
        unprocessedDown中记录着某电梯将要进行但是还没有开始进行的下降请求
        seqRise.append存放电梯中向上的序列的列表
        seqDrop.append存放电梯中向下的序列的列表
    """
    def __init__(self, ui):
        self.ui = ui
        self.goingUp = {}
        self.goingDown = {}
        self.lastTimeRise = {}
        self.lastTimeDrop = {}
        self.location = {}

        #初始化状态都是false
        for i in range(1, 6):
            self.goingUp[i] = False
            self.goingDown[i] = False
            self.lastTimeRise[i] = False
            self.lastTimeDrop[i] = False
            self.location[i] = 1

        self.unprocessedUp = []
        self.unprocessedDown = []
        self.seqRise = []
        self.seqDrop = []
        for i in range(6):
            self.unprocessedUp.append([0] * 21)
        for j in range(6):
            self.unprocessedDown.append([0] * 21)
        for k in range(6):
            self.seqRise.append([])
        for l in range(6):
            self.seqDrop.append([])

        """
            分别将向上的电梯按钮、向下的电梯按钮、电梯内的数字按钮与监听函数绑定
            然后对线程进行加载
        """
        for i in range(1, 20):
            self.ui.upBtn[i].clicked.connect(functools.partial(self.uplinkButtonListener, i))
        for i in range(2, 21):
            self.ui.downBtn[i].clicked.connect(functools.partial(self.downlinkButtonListener, i))
        for i in range(1, 6):
            for j in range(1, 21):
                self.ui.numBtn[i][j].clicked.connect(functools.partial(self.numButtonListner, i, j))
        for i in range(1, 6):
            self.thread(i)

    """
        RisingDistance中记录着发出上升请求时当有一层楼的按钮被按后，此时所有的电梯都开始计算自己的距离，初始化为30.
        fallingDistance中记录着发出下降请求时当有一层楼的按钮被按后，此时所有的电梯都开始计算自己的距离，初始化为30.
        upRequest中记录着被按的楼层是否在电梯当前位置的上方或者是本层
        downRequest中记录着被按的楼层是否在电梯当前位置的下方或者是本层
        当某楼层有上行或下行请求发出时，先考虑每部电梯在完成当前序列的过程中能否响应该请求，计算出符合此条件的电梯的响应距离，再考虑
        剩余电梯从其当前位置到序列终点与终点到该请求位置的响应距离之和，最后比较每部电梯的响应距离，将该请求分配给具有最短响应距离一
        部电梯。
    """
    def uplinkButtonListener(self, buttonSelection):
        self.ui.upBtn[buttonSelection].setStyleSheet("QPushButton{border-image: url(res/up_pressed.png)}")
        RisingDistance = [30, 30, 30, 30, 30, 30]

        upRequest = {}

        i = 1
        while i < 6:
            upRequest[i] = False
            if (buttonSelection - self.location[i]) >= 0:
                upRequest[i] = True
            i += 1

        i = 1
        while i < 6:
            if self.goingUp[i] == True:
                if upRequest[i]:
                    RisingDistance[i] = abs(buttonSelection - self.location[i])
                else:
                    RisingDistance[i] = abs(self.location[i] - self.seqRise[i][len(self.seqRise[i]) - 1]) \
                                        + abs(
                        buttonSelection - self.seqRise[i][len(self.seqRise[i]) - 1])  # 当前位置距终点距离 + 终点距请求位置距离

            elif self.goingUp[i] == False and self.goingDown[i] == False:
                RisingDistance[i] = abs(buttonSelection - self.location[i])

            elif self.goingDown[i] == True:
                RisingDistance[i] = abs(self.location[i] - self.seqDrop[i][len(self.seqDrop[i]) - 1]) \
                                    + abs(
                    buttonSelection - self.seqDrop[i][len(self.seqDrop[i]) - 1])  # 当前位置距终点距离 + 终点距请求位置距离

            i += 1
        quickestElevator = RisingDistance.index(min(RisingDistance))  # 最快到达的电梯的序号

        if self.goingUp[quickestElevator] == True:
            if upRequest[quickestElevator]:
                self.seqRise[quickestElevator].append(buttonSelection)
                self.seqRise[quickestElevator] = list(set(self.seqRise[quickestElevator]))
                self.seqRise[quickestElevator].sort() # 对发出请求的楼层进行排序
            else:
                self.unprocessedUp[quickestElevator][buttonSelection] = 1

        elif self.goingUp[quickestElevator] == False and self.goingDown[quickestElevator] == False:
            if upRequest[quickestElevator]:
                self.seqRise[quickestElevator].append(buttonSelection)
                self.seqRise[quickestElevator] = list(set(self.seqRise[quickestElevator]))
                self.seqRise[quickestElevator].sort() # 对发出请求的楼层进行排序
            else:
                self.seqDrop[quickestElevator] = list(set(self.seqDrop[quickestElevator]))
                self.seqDrop[quickestElevator].sort()
                self.seqDrop[quickestElevator].reverse()  # 对发出请求的楼层进行逆序
                self.unprocessedUp[quickestElevator][buttonSelection] = 1

        elif self.goingDown[quickestElevator] == True:
            self.unprocessedUp[quickestElevator][buttonSelection] = 1


    def downlinkButtonListener(self, buttonSelection):
        self.ui.downBtn[buttonSelection].setStyleSheet("QPushButton{border-image: url(res/down_pressed.png)}")
        fallingDistance = [30, 30, 30, 30, 30, 30]
        downRequest = {}
        i = 1
        while i < 6:
            downRequest[i] = False
            if (buttonSelection - self.location[i]) <= 0:
                downRequest[i] = True
            i += 1

        i = 1

        #与上行时相同
        while i < 6:
            if self.goingUp[i] == False and self.goingDown[i] == True:
                if downRequest[i]:
                    fallingDistance[i] = abs(self.location[i] - buttonSelection)
                else:
                    fallingDistance[i] = abs(
                        self.location[i] - self.seqDrop[i][len(self.seqDrop[i]) - 1]) \
                                          + abs(buttonSelection - self.seqDrop[i][
                        len(self.seqDrop[i]) - 1])

            elif self.goingUp[i] == False and self.goingDown[i] == False:
                fallingDistance[i] = abs(self.location[i] - buttonSelection)

            elif self.goingUp[i] == True and self.goingDown[i] == False:
                fallingDistance[i] = abs(self.location[i] - self.seqRise[i][len(self.seqRise[i]) - 1]) \
                                      + abs(
                    buttonSelection - self.seqRise[i][len(self.seqRise[i]) - 1])
            i += 1

        quickestElevator = fallingDistance.index(min(fallingDistance))
        if self.goingUp[quickestElevator] == False and self.goingDown[quickestElevator] == True:  # 下行状态
            if downRequest[quickestElevator]:
                self.seqDrop[quickestElevator].append(buttonSelection)
                self.seqDrop[quickestElevator] = list(set(self.seqDrop[quickestElevator]))
                self.seqDrop[quickestElevator].sort()
                self.seqDrop[quickestElevator].reverse()  # 对发出请求的楼层进行逆序
            else:
                self.unprocessedDown[quickestElevator][buttonSelection] = 1

        elif self.goingUp[quickestElevator] == False and self.goingDown[quickestElevator] == False:
            if downRequest[quickestElevator]:
                self.seqDrop[quickestElevator].append(buttonSelection)
                self.seqDrop[quickestElevator] = list(set(self.seqDrop[quickestElevator]))
                self.seqDrop[quickestElevator].sort()
                self.seqDrop[quickestElevator].reverse()  # 对发出请求的楼层进行逆序
            else:
                self.seqRise[quickestElevator].append(buttonSelection)
                self.seqRise[quickestElevator] = list(set(self.seqRise[quickestElevator]))
                self.seqRise[quickestElevator].sort() # 对发出请求的楼层进行排序
                self.unprocessedDown[quickestElevator][buttonSelection] = 1

        elif self.goingUp[quickestElevator] == True and self.goingDown[quickestElevator] == False:
            self.unprocessedDown[quickestElevator][buttonSelection] = 1


    """
        定义方法用于监听电梯楼层中的数字按钮，传入的参数分别为quickestElevator，buttonSelection，其中，quickestElevator代表了最快到达的
        电梯序号，buttonSelection代表了电梯中被按到的楼层号。
        电梯在静止状态时，请求在下方加入下行序列，在上方加入下行序列，否则不做相应
        电梯在上行状态时，请求在上方加入下行序列，否则不做相应
        电梯在下行状态时，请求在下方加入下行序列，否则不做相应
    """
    def numButtonListner(self, quickestElevator, buttonSelection):
        if self.goingUp[quickestElevator] == False and self.goingDown[quickestElevator] == False:
            if self.location[quickestElevator] > buttonSelection:
                self.ui.numBtn[quickestElevator][buttonSelection].setStyleSheet(
                    "QPushButton{border-image: url(res/" + str(buttonSelection) + "_pressed.png)}")
                self.seqDrop[quickestElevator].append(buttonSelection)
                self.seqDrop[quickestElevator] = list(set(self.seqDrop[quickestElevator]))
                self.seqDrop[quickestElevator].sort()
                self.seqDrop[quickestElevator].reverse()
            if self.location[quickestElevator] < buttonSelection:
                self.ui.numBtn[quickestElevator][buttonSelection].setStyleSheet(
                    "QPushButton{border-image: url(res/" + str(buttonSelection) + "_pressed.png)}")
                self.seqRise[quickestElevator].append(buttonSelection)
                self.seqRise[quickestElevator] = list(set(self.seqRise[quickestElevator]))
                self.seqRise[quickestElevator].sort()

        elif self.goingUp[quickestElevator] == True and self.goingDown[quickestElevator] == False:
            if self.location[quickestElevator] < buttonSelection:
                self.ui.numBtn[quickestElevator][buttonSelection].setStyleSheet(
                    "QPushButton{border-image: url(res/" + str(buttonSelection) + "_pressed.png)}")
                self.seqRise[quickestElevator].append(buttonSelection)
                self.seqRise[quickestElevator] = list(set(self.seqRise[quickestElevator]))
                self.seqRise[quickestElevator].sort()

        elif self.goingUp[quickestElevator] == False and self.goingDown[quickestElevator] == True:
            if self.location[quickestElevator] > buttonSelection:
                self.ui.numBtn[quickestElevator][buttonSelection].setStyleSheet(
                    "QPushButton{border-image: url(res/" + str(buttonSelection) + "_pressed.png)}")
                self.seqDrop[quickestElevator].append(buttonSelection)
                self.seqDrop[quickestElevator] = list(set(self.seqDrop[quickestElevator]))
                self.seqDrop[quickestElevator].sort()
                self.seqDrop[quickestElevator].reverse()

        else:
            print("error")

    """
        创建线程
    """
    def thread(self, quickestElevator):
        thrd = threading.Thread(target=functools.partial(self.elevatorAnimation, quickestElevator))
        thrd.setDaemon(True)
        thrd.start()

    """
        对电梯的上行序列动画进行处理，quickestElevator为最快到达的电梯
        先将电梯当前上行状态设为True，保存在goingUp[quickestElevator]中
        创建变量firstUpTask，其中保存电梯在上行中将要处理的第一个任务，计算与当前所在的位置相差的层数，然后对电梯的标签和楼层显示进行更新，当上行
        第一个任务有更新时，则更新当前位置与上行序列的第一个任务相差的层数然后进行循环。处理完该楼层的任务后，将其从序列中删除，将本次的运行状态存储到lastTimeRise
        集合中，然后将电梯的上行状态设置为False
    """
    def elevatorUpAnim(self, quickestElevator):
        while len(self.seqRise[quickestElevator]):
            self.goingUp[quickestElevator] = True
            firstUpTask = self.seqRise[quickestElevator][0]
            j = abs(
                self.seqRise[quickestElevator][0] - self.location[quickestElevator])
            i = 1
            while i <= j:
                if firstUpTask == self.seqRise[quickestElevator][0]:
                    time.sleep(0.5)
                    self.location[quickestElevator] = self.location[quickestElevator] + 1
                    self.ui.elevatorPix[quickestElevator].setGeometry(
                        QtCore.QRect((quickestElevator-1)* 130 + 230, 660 - 30 * self.location[quickestElevator], 35, 35))
                    self.num = '当前楼层: {}'.format(self.location[quickestElevator])
                    self.ui.locLabel[quickestElevator].setText(self.num)
                else:
                    j = abs(self.seqRise[quickestElevator][0] - self.location[
                        quickestElevator])
                    firstUpTask = self.seqRise[quickestElevator][0]
                    i = 0
                i += 1

            time.sleep(0.5)

            if self.seqRise[quickestElevator][0] < 20:
                self.ui.upBtn[self.seqRise[quickestElevator][0]].setStyleSheet(self.ui.upBtnStyle)
            self.ui.numBtn[quickestElevator][self.seqRise[quickestElevator][0]].setStyleSheet(
                "QPushButton{border-image: url(res/" + str(self.seqRise[quickestElevator][0]) + "_hover.png)}"
                "QPushButton:hover{border-image: url(res/" + str(self.seqRise[quickestElevator][0]) + ".png)}"
                "QPushButton:pressed{border-image: url(res/" + str(self.seqRise[quickestElevator][0]) +
                "_pressed.png)}"
            )

            del self.seqRise[quickestElevator][0]
        self.lastTimeRise[quickestElevator] = self.goingUp[quickestElevator]
        self.goingUp[quickestElevator] = False

    """
        对电梯的下行序列动画进行处理，quickestElevator为最快到达的电梯
        先将电梯当前下行状态设为True，保存在goingDown[quickestElevator]中
        创建变量firstDownTask，其中保存电梯在下行中将要处理的第一个任务，计算与当前所在的位置相差的层数，然后对电梯的标签和楼层显示进行更新，当下行
        第一个任务有更新时，则更新当前位置与下行序列的第一个任务相差的层数然后进行循环。处理完该楼层的任务后，将其从序列中删除，将本次的运行状态存储到lastTimeDrop
        集合中，然后将电梯的下行状态设置为False
    """
    def elevatorDownAnim(self, quickestElevator):
        while len(self.seqDrop[quickestElevator]):
            self.goingDown[quickestElevator] = True
            firstDownTask = self.seqDrop[quickestElevator][0]
            j = abs(
                self.seqDrop[quickestElevator][0] - self.location[quickestElevator])
            i = 1
            while i <= j:
                if firstDownTask == self.seqDrop[quickestElevator][0]:
                    time.sleep(0.5)
                    self.location[quickestElevator] = self.location[quickestElevator] - 1
                    self.ui.elevatorPix[quickestElevator].setGeometry(
                        QtCore.QRect((quickestElevator-1) * 130 + 230, 660 - 30 * self.location[quickestElevator], 35, 35))
                    self.num = '当前楼层: {}'.format(self.location[quickestElevator])
                    self.ui.locLabel[quickestElevator].setText(self.num)
                else:
                    j = abs(self.seqDrop[quickestElevator][0] - self.location[quickestElevator])
                    firstDownTask = self.seqDrop[quickestElevator][0]
                    i = 0
                i = i + 1

            time.sleep(0.5)

            if self.seqDrop[quickestElevator][0] > 1:
                self.ui.downBtn[self.seqDrop[quickestElevator][0]].setStyleSheet(self.ui.downBtnStyle)
            self.ui.numBtn[quickestElevator][self.seqDrop[quickestElevator][0]].setStyleSheet(
                "QPushButton{border-image: url(res/" + str(self.seqDrop[quickestElevator][0]) + "_hover.png)}"
                "QPushButton:hover{border-image: url(res/" +
                str(self.seqDrop[quickestElevator][0]) + ".png)}"
                "QPushButton:pressed{border-image: url(res/" +
                str(self.seqDrop[quickestElevator][0]) + "_pressed.png)}")
            del self.seqDrop[quickestElevator][0]
        self.lastTimeDrop[quickestElevator] = self.goingDown[quickestElevator]
        self.goingDown[quickestElevator] = False

    """
        当电梯上行状态结束后，对产生但未做处理的请求进行处理，如果为下行请求，则该请求可能出现在任意的位置。若为上行请求，则只可以出现在下方。
        对未处理的下行请求做处理时，应进行倒序处理，对上方存在执行动作时产生的但未处理的下行请求做处理时，将最高楼层的下行请求加入上行序列,继续上行。
        对上方不存在执行动作时产生的但未处理的请求做处理时，将记录的上方的上行请求加入上行序列，开始上行。
        对未处理的上行请求做处理时，只可能出现在下方，应当做正序处理，将最底楼层的下行请求加入下行序列,开始下行。
    """

    def riseToStop(self, quickestElevator):
        i = 20
        while i >= 1:
            if self.unprocessedDown[quickestElevator][i] == 1:
                if i > self.location[quickestElevator]:
                    self.seqRise[quickestElevator].append(i)
                    self.seqRise[quickestElevator] = list(set(self.seqRise[quickestElevator]))
                    self.goingUp[quickestElevator] = True
                    break
                self.unprocessedDown[quickestElevator][i] = 0
                self.seqDrop[quickestElevator].append(i)
                self.seqDrop[quickestElevator] = list(set(self.seqDrop[quickestElevator]))
                self.seqDrop[quickestElevator].sort()
                self.seqDrop[quickestElevator].reverse()
                self.goingDown[quickestElevator] = True
            i -= 1

        if self.goingDown[quickestElevator] == False and self.goingUp[quickestElevator] == False:
            for i in range(1, 21):
                if self.unprocessedUp[quickestElevator][i] == 1:
                    self.seqDrop[quickestElevator].append(i)
                    self.seqDrop[quickestElevator] = list(set(self.seqDrop[quickestElevator]))
                    self.goingDown[quickestElevator] = True
                    break

    """
        当电梯下行状态结束后，对产生但未做处理的请求进行处理，如果为上行请求，则该请求可能出现在任意的位置。若为下行请求，则只可以出现在上方。
        对未处理的上行请求做处理时，应进行正序处理，对下方存在执行动作时产生的但未处理的上行请求做处理时，将最低楼层的上行请求加入下行序列,继续下行。
        对下方不存在执行动作时产生的但未处理的请求做处理时，将记录的上方的上行请求加入上行序列，开始上行。
        对未处理的下行请求做处理时，只可能出现在上方，应当做倒序处理，将最高楼层的下行请求加入上行序列,开始上行。
    """

    def dropToStop(self, quickestElevator):
        i = 1
        while i <= 20:
            if self.unprocessedUp[quickestElevator][i] == 1:
                if i < self.location[quickestElevator]:
                    self.seqDrop[quickestElevator].append(i)
                    self.seqDrop[quickestElevator] = list(set(self.seqDrop[quickestElevator]))
                    self.goingDown[quickestElevator] = True
                    break
                self.unprocessedUp[quickestElevator][i] = 0
                self.seqRise[quickestElevator].append(i)
                self.seqRise[quickestElevator] = list(set(self.seqRise[quickestElevator]))
                self.seqRise[quickestElevator].sort()
                self.goingUp[quickestElevator] = True
            i += 1

        if self.goingUp[quickestElevator] == False and self.goingDown[quickestElevator] == False:
            i = 20
            while i >= 1:
                if self.unprocessedDown[quickestElevator][i] == 1:
                    self.seqRise[quickestElevator].append(i)
                    self.seqRise[quickestElevator] = list(set(self.seqRise[quickestElevator]))
                    self.goingUp[quickestElevator] = True
                    break
                i -= 1

    """
        动画执行完后将未能执行的数据处理。
        分为电梯上次静止、上次上行、上次下行三种情况进行处理
    """
    def animationEnd(self, quickestElevator):
        if self.lastTimeRise[quickestElevator] == False and self.lastTimeDrop[quickestElevator] == False:
            self.dropToStop(quickestElevator)

        elif self.lastTimeRise[quickestElevator] == True and self.lastTimeDrop[quickestElevator] == False:
            self.riseToStop(quickestElevator)

        elif self.lastTimeRise[quickestElevator] == False and self.lastTimeDrop[quickestElevator] == True:
            self.dropToStop(quickestElevator)

    """
        分别加载电梯静止、上行、下行的动画。
    """
    def elevatorAnimation(self, quickestElevator):
        while 1:
            if self.goingUp[quickestElevator] == False and self.goingDown[quickestElevator] == False:
                self.elevatorUpAnim(quickestElevator)
                self.animationEnd(quickestElevator)
                self.elevatorDownAnim(quickestElevator)
                self.animationEnd(quickestElevator)

            elif self.goingUp[quickestElevator] == True and self.goingDown[quickestElevator] == False:  # 电梯处于上行状态
                self.elevatorUpAnim(quickestElevator)
                self.animationEnd(quickestElevator)

            elif self.goingUp[quickestElevator] == False and self.goingDown[quickestElevator] == True:  # 电梯处于下行状态
                self.elevatorDownAnim(quickestElevator)
                self.animationEnd(quickestElevator)