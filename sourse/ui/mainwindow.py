from PyQt5 import QtGui, QtWidgets, uic


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("sourse/ui/mainwindow.ui", self)  # Load the .ui file
        # self.setWindowIcon(QtGui.QIcon("assets/icon_1.png"))

        self.show()
