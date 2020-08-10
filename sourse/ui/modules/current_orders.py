from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import datetime
import typing


class CurrentOrdersModule(BaseUIModule):
    def _create_widgets(self):
        self.layout = QtWidgets.QHBoxLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Current Orders")
        self.base_widget.setLayout(self.layout)

        self._current_id = 0
        self._order_dict = {}

        self.table = QtWidgets.QTableWidget(len(self._order_dict), 5)

        self.table.setSortingEnabled(False)
        self.table.setHorizontalHeaderLabels(["id", "Time", "Side", "Price", "Volume"])
        self.table.verticalHeader().hide()

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)

        self.layout.addWidget(self.table)

    def add_order(self, order_id: str, price: float, volume: float) -> int:
        self._current_id += 1
        order_id = self._current_id

        self._order_dict[order_id] = Order(price=price, volume=volume)

        self.table.setRowCount(len(self._order_dict))

        self.table.setItem(len(self._order_dict) - 1, 0, self.createItem(str(order_id)))
        for i, value in enumerate(self._order_dict[order_id].to_dict().values()):
            self.table.setItem(
                len(self._order_dict) - 1, i + 1, self.createItem(str(value))
            )

        return order_id

    def remove_order(self, order_id: int) -> None:
        del self._order_dict[order_id]
        self.table.removeRow(order_id - 1)

    def createItem(self, text):
        tableWidgetItem = QtWidgets.QTableWidgetItem(text)
        tableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        return tableWidgetItem


class Order:
    def __init__(self, price: float, volume: float):
        self.price = price
        self.volume = volume

        self.side = "Buy" if volume > 0 else "Sell"
        self.date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def to_dict(self):
        return dict(
            time=self.date, side=self.side, price=self.price, volume=abs(self.volume)
        )

