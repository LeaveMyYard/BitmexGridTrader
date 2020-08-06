from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sourse.ui.modules as UiModules
import pyqtgraph
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

        self.setting_templates = UiModules.SettingTemplatesModule(
            self.bottom_right_dockwidget
        )

        self.setting_templates.template_selected.connect(
            lambda name, settings: self.current_settings.on_template_loaded(
                name, settings
            )
        )
        self.current_settings.templates_updated.connect(
            self.setting_templates.refresh_templates
        )
        self.current_settings.settings_changed.connect(
            self.setting_templates.reset_load_buttons
        )

        self.current_orders = UiModules.CurrentOrdersModule(self.bottom_dockwidget)

        self.graphWidget = pyqtgraph.PlotWidget()
        self.graphWidget.setBackground("#19232d")  # 25 35 45
        self.setCentralWidget(self.graphWidget)

        data = [  ## fields are (time, open, close, min, max).
            (i, i + 1, i, i - 10, i + 10) for i in range(100)
        ]

        item = CandlestickItem(data)
        self.graphWidget.addItem(item)
        self.graphWidget.setWindowTitle("pyqtgraph example: customGraphicsItem")

        self.show()


class CandlestickItem(pyqtgraph.GraphicsObject):
    def __init__(self, data):
        pyqtgraph.GraphicsObject.__init__(self)
        self.data = data  ## data must have fields: time, open, close, min, max
        self.generatePicture()

    def generatePicture(self):
        ## pre-computing a QPicture object allows paint() to run much more quickly,
        ## rather than re-drawing the shapes every time.
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pyqtgraph.mkPen("w"))
        w = (self.data[1][0] - self.data[0][0]) / 3.0
        for (t, open, close, min, max) in self.data:
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            if open > close:
                p.setBrush(pyqtgraph.mkBrush("r"))
            else:
                p.setBrush(pyqtgraph.mkBrush("g"))
            p.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        ## boundingRect _must_ indicate the entire area that will be drawn on
        ## or else we will get artifacts and possibly crashing.
        ## (in this case, QPicture does all the work of computing the bouning rect for us)
        return QtCore.QRectF(self.picture.boundingRect())
