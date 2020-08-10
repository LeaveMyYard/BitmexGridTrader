from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph
import pandas as pd
import typing


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

        t = self.data["id"]
        open = self.data["Open"]
        high = self.data["High"]
        low = self.data["Low"]
        close = self.data["Close"]
        # p.setPen(pyqtgraph.mkPen("#ffffff00"))

        if open > close:
            p.setBrush(pyqtgraph.mkBrush("#EF5350"))
            p.setPen(pyqtgraph.mkPen("#EF5350"))
        else:
            p.setBrush(pyqtgraph.mkBrush("#26A69A"))
            p.setPen(pyqtgraph.mkPen("#26A69A"))
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


class Chart(QtCore.QObject):
    def __init__(self, parent: QtWidgets.QMainWindow):
        super().__init__(parent)

        self.graphWidget = pyqtgraph.PlotWidget()
        self.graphWidget.setBackground("#19232d")  # 25 35 45
        parent.setCentralWidget(self.graphWidget)

        self.graphWidget.showGrid(True, True)

        self._hist: pd.DataFrame
        self._drawn_candles: typing.Dict[int, CandlestickItem] = {}
        self._left_candle = 0
        self._right_candle = 0

        self.__prev_rect: QtCore.QRectF = None
        self._grid_lines: typing.List[pyqtgraph.GraphicsObject] = []
        self.graphWidget.sigRangeChanged.connect(self._on_range_changed)

        # curr_price = self._hist.iloc[-1]["Close"]
        # self.add_grid(
        #     [curr_price + i * 5 for i in range(10)],
        #     [curr_price - i * 5 for i in range(10)],
        # )

    def draw_historical_data(self, hist_data: pd.DataFrame):
        self._hist = hist_data
        self._hist["id"] = list(range(len(self._hist)))

        for i, row in self._hist.iloc[-100:].iterrows():
            self._draw_candle(i)

        curr_price = self._hist.iloc[-1]["Close"]
        curr_id = self._hist.iloc[-1]["id"]

        width = 100

        prices = [
            (min(row), max(row))
            for i, row in (
                self._hist[["Open", "High", "Low", "Close"]]
                .iloc[curr_id - width - 1 : -1]
                .iterrows()
            )
        ]

        min_price, max_price = (
            min(prices, key=lambda x: x[0])[0],
            max(prices, key=lambda x: x[1])[1],
        )

        height = 2 * max(abs(min_price - curr_price), abs(max_price - curr_price))

        rect = QtCore.QRectF(
            curr_id - width + 1, curr_price - height / 2, width, height
        )

        self.graphWidget.sigRangeChanged.disconnect(self._on_range_changed)
        self.graphWidget.setRange(rect)
        self.graphWidget.sigRangeChanged.connect(self._on_range_changed)

    def _draw_candle(self, num: int) -> typing.Optional[CandlestickItem]:
        if num in self._drawn_candles:
            self.graphWidget.removeItem(self._drawn_candles[num])

        try:
            self._drawn_candles[num] = item = CandlestickItem(self._hist.iloc[num])
        except IndexError:
            return None

        self.graphWidget.addItem(item)
        return item

    def _undraw_candle(self, num: int) -> None:
        if num not in self._drawn_candles:
            return

        item = self._drawn_candles[num]
        self.graphWidget.removeItem(item)
        self._drawn_candles.pop(num, 0)

    def _id_is_viewed(self, time: float) -> bool:
        return time >= self._left_candle and time <= self._right_candle

    @QtCore.pyqtSlot(object)
    def _on_range_changed(self, pos):
        rect: QtCore.QRectF = pos.viewRect()

        if rect.width() > 1500:
            if self.__prev_rect.width() > 1500:
                self.__prev_rect.setWidth(1500)
            self.graphWidget.sigRangeChanged.disconnect(self._on_range_changed)
            self.graphWidget.setRange(self.__prev_rect)
            self.graphWidget.sigRangeChanged.connect(self._on_range_changed)
            return

        x = int(rect.x())

        if x < self._left_candle:
            for i in range(x, self._left_candle + 1):
                self._draw_candle(i)
                self._left_candle = min(self._left_candle, i)
        elif x > self._left_candle:
            for i in range(self._left_candle + 1, x + 1):
                self._undraw_candle(i)
                self._left_candle = max(self._left_candle, i)

        x = int(rect.x() + rect.width())

        if x > self._right_candle:
            for i in range(self._right_candle, x + 1):
                self._draw_candle(i)
                self._right_candle = max(self._right_candle, i)
        elif x < self._right_candle:
            for i in range(x + 1, self._right_candle + 1):
                self._undraw_candle(i)
                self._right_candle = min(self._right_candle, i)

        self.__prev_rect = rect

    def get_current_candle_id(self) -> int:
        return self._hist["id"].iloc[-1]

    def add_grid(self, buy_grid: typing.List[float], sell_grid: typing.List[float]):
        for buy_order in buy_grid:
            now_id = self.get_current_candle_id()
            line = self.graphWidget.plot(
                x=[now_id, now_id + 1],
                y=[buy_order] * 2,
                pen=pyqtgraph.mkPen("#EF5350"),
            )

        for sell_order in sell_grid:
            now_id = self.get_current_candle_id()
            line = self.graphWidget.plot(
                x=[now_id, now_id + 1],
                y=[sell_order] * 2,
                pen=pyqtgraph.mkPen("#26A69A"),
            )

    def add_candle(self, candle_data: typing.Mapping[str, float]) -> None:
        new_id = self._hist["id"].iloc[-1] + 1
        data = pd.DataFrame(
            {
                "id": new_id,
                "Open": candle_data["Open"],
                "High": candle_data["High"],
                "Low": candle_data["Low"],
                "Close": candle_data["Close"],
                "Volume": candle_data["Volume"],
            },
            index=[0],
        )
        self._hist = self._hist.append(data)

        if self._id_is_viewed(new_id):
            self._draw_candle(new_id)
