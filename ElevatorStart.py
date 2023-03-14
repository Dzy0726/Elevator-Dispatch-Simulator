from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtGui import QIcon
from Elevator.ElevatorUI import UiMainWindow
from Elevator.ElevatorRun import Elevator
import sys




class myElevator(QtWidgets.QMainWindow):

    def __init__(self):
        super(myElevator, self).__init__()
        self.myCommand = " "
        self.ui = UiMainWindow()
        self.ui.setUI(self)
        self.schedule = Elevator(self.ui)

if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #确保多平台的可移植性
    app = QtWidgets.QApplication([])
    application = myElevator()
    app.setWindowIcon(QIcon("border-img url(res/Icon.png)"))
    application.show()
    sys.exit(app.exec_())
