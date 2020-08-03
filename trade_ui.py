import sys

import qdarkstyle
from sourse.ui.mainwindow import MainWindow
from PyQt5 import QtWidgets


def main():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    app.exec_()


if __name__ == "__main__":
    main()

