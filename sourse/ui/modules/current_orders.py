from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from PyQt5 import QtWidgets
import datetime
import typing


class CurrentOrdersModule(IQDockWidgetModule):
    def _create_widgets(self):
        self.layout = QtWidgets.QHBoxLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Current Orders")
        self.base_widget.setLayout(self.layout)

        self._current_id = 0
        self._order_dict = {}

        self.table = QtWidgets.QTableWidget(len(self._order_dict) + 100, 5)
        self.table.setSortingEnabled(True)
        self.table.setHorizontalHeaderLabels(["id", "Time", "Side", "Price", "Volume"])

        for i in range(10):
            self.add_order(i, i)

        self.layout.addWidget(self.table)

    def add_order(self, price: float, volume: float) -> int:
        self._current_id += 1
        order_id = self._current_id

        self._order_dict[order_id] = Order(price=price, volume=volume)

        self.table.setItem(
            len(self._order_dict), 0, QtWidgets.QTableWidgetItem(str(order_id))
        )
        for i, value in enumerate(self._order_dict[order_id].to_dict().values()):
            self.table.setItem(
                len(self._order_dict), i + 1, QtWidgets.QTableWidgetItem(str(value))
            )

        # self.table.setItem(1, 1, QtWidgets.QTableWidgetItem(str(1)))
        # self.table.setItem(1, 2, QtWidgets.QTableWidgetItem(str(2)))
        # self.table.setItem(1, 3, QtWidgets.QTableWidgetItem(str(3)))
        # self.table.setItem(1, 4, QtWidgets.QTableWidgetItem(str(4)))
        # self.table.setItem(1, 5, QtWidgets.QTableWidgetItem(str(5)))

        return order_id

    def remove_order(self, order_id: int) -> None:
        del self._order_dict[order_id]


class Order:
    def __init__(self, price: float, volume: float):
        self.price = price
        self.volume = volume

        self.side = "Buy" if volume > 0 else "Sell"
        self.date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def to_dict(self):
        return dict(
            time=self.date, side=self.side, price=self.price, volume=self.volume
        )

