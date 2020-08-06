from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph
import pandas as pd
import typing


class Chart(QtCore.QObject):
    def __init__(self, parent: QtWidgets.QMainWindow):
        super().__init__(parent)

        self.graphWidget = pyqtgraph.PlotWidget()
        self.graphWidget.setBackground("#19232d")  # 25 35 45
        parent.setCentralWidget(self.graphWidget)

        data = [  ## fields are (time, open, close, min, max).
            (i, i + 1, i, i - 10, i + 10) for i in range(100)
        ]

        self.graphWidget.showGrid(True, True)

        self._hist: pd.DataFrame = self._load_hist().iloc[:100]

        for i, row in self._hist.iterrows():
            item = CandlestickItem(row)
            self.graphWidget.addItem(item)

        self.graphWidget.sigRangeChanged.connect(self._on_range_changed)

    def _load_hist(self) -> pd.DataFrame:
        return pd.read_csv(
            r"C:\Users\blackbox1\Documents\GitHub\CUDA-Trading-Optimizer\data\binance_1d.csv"
        )

    @QtCore.pyqtSlot(object)
    def _on_range_changed(self, pos):
        rect: QtCore.QRectF = pos.viewRect()
        print(rect)


class CandlestickItem(pyqtgraph.GraphicsObject):
    def __init__(self, data: typing.Mapping[str, float], candle_width: float = 0.333):
        pyqtgraph.GraphicsObject.__init__(self)
        self.data = data
        self.candle_width = candle_width

        self.generatePicture()

    def generatePicture(self):
        ## pre-computing a QPicture object allows paint() to run much more quickly,
        ## rather than re-drawing the shapes every time.
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)

        t = self.data["Unnamed: 0"]
        open = self.data["Open"]
        high = self.data["High"]
        low = self.data["Low"]
        close = self.data["Close"]
        # p.setPen(pyqtgraph.mkPen("#ffffff00"))

        if open > close:
            p.setBrush(pyqtgraph.mkBrush("#FF4500"))
            p.setPen(pyqtgraph.mkPen("#FF4500"))
        else:
            p.setBrush(pyqtgraph.mkBrush("#00FF00"))
            p.setPen(pyqtgraph.mkPen("#00FF00"))
        p.drawLine(QtCore.QPointF(t, low), QtCore.QPointF(t, high))
        p.drawRect(
            QtCore.QRectF(
                t - self.candle_width, open, self.candle_width * 2, close - open
            )
        )

        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        ## boundingRect _must_ indicate the entire area that will be drawn on
        ## or else we will get artifacts and possibly crashing.
        ## (in this case, QPicture does all the work of computing the bouning rect for us)
        return QtCore.QRectF(self.picture.boundingRect())
