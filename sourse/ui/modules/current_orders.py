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

        self.table = QtWidgets.QTableWidget(len(self._order_dict), 6)

        self.table.setSortingEnabled(True)
        self.table.setHorizontalHeaderLabels(
            ["id", "Time", "Side", "Price", "Volume", "Status"]
        )
        self.table.verticalHeader().hide()

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)

        self.layout.addWidget(self.table)

    def add_order(self, order_id: str, price: float, volume: float, status: str) -> str:
        if order_id in self._order_dict.keys():
            self._edit_order(
                order_id=order_id, price=price, volume=volume, status=status
            )

        self.table.setSortingEnabled(False)

        self._current_id += 1
        order_id = self._current_id

        self._order_dict[order_id] = Order(price=price, volume=volume)

        self.table.setRowCount(len(self._order_dict))

        self.table.setItem(len(self._order_dict) - 1, 0, self.createItem(str(order_id)))
        for i, value in enumerate(self._order_dict[order_id].to_dict().values()):
            self.table.setItem(
                len(self._order_dict) - 1, i + 1, self.createItem(str(value))
            )

        self.table.setSortingEnabled(True)

        return order_id

    def _edit_order(
        self, order_id: str, price: float, volume: float, status: str
    ) -> str:
        self.table.setSortingEnabled(False)

        tmp_order = self._order_dict[order_id]
        order_index = list(self._order_dict.keys()).index(order_id)

        if price != tmp_order.price:
            self._order_dict[order_id].price = price
            self.table.item(3, order_index).setText(str(price))
        if volume != tmp_order.volume:
            self._order_dict[order_id].volume = volume
            self.table.item(4, order_index).setText(str(volume))
        if status != tmp_order.status:
            self._order_dict[order_id].status = status
            self.table.item(5, order_index).setText(str(status))

        self.table.setSortingEnabled(True)

        return order_id

    def remove_order(self, order_id: int) -> None:
        self.table.setSortingEnabled(False)

        del self._order_dict[order_id]
        self.table.removeRow(list(self._order_dict.keys()).index(order_id))

        self.table.setSortingEnabled(True)

    def remove_all_orders(self) -> None:
        self.table.setSortingEnabled(False)

        self._order_dict = {}
        self.table.setRowCount(0)

        self.table.setSortingEnabled(True)

    @staticmethod
    def createItem(text: str) -> QtWidgets.QTableWidgetItem:
        tableWidgetItem = QtWidgets.QTableWidgetItem(text)
        tableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        return tableWidgetItem


class Order:
    def __init__(self, price: float, volume: float, status: str = None):
        self.price = price
        self.volume = volume

        self.side = "Buy" if volume > 0 else "Sell"
        self.time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.status = status

    def to_dict(self):
        return dict(
            time=self.time,
            side=self.side,
            price=self.price,
            volume=abs(self.volume),
            status=self.status,
        )
