from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sourse.ui.modules as UiModules
import typing


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("sourse/ui/mainwindow.ui", self)  # Load the .ui file
        # # self.setWindowIcon(QtGui.QIcon("assets/icon_1.png"))

        self.top_left_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget"
        )
        self.bottom_left_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget_2"
        )
        self.top_right_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget_3"
        )
        self.bottom_right_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget_4"
        )
        self.bottom_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget_5"
        )

        self.current_settings = UiModules.CurrentSettingsModule(
            self.top_right_dockwidget
        )

        self.show()
