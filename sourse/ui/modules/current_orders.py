from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from sourse.exchange_handlers import AbstractExchangeHandler
import datetime
import dataclasses
import typing


class CurrentOrdersModule(BaseUIModule):
    def _create_widgets(self):
        self.layout = QtWidgets.QHBoxLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Current Orders")
        self.base_widget.setLayout(self.layout)

        self._order_dict = {}

        self.horizontalHeaderLabelsList = [
            "Order id",
            "Client order id",
            "Status",
            "Price",
            "Average price",
            "Fee",
            "Fee asset",
            "Volume",
            "Volume realized",
            "Time",
        ]

        self.table = QtWidgets.QTableWidget(len(self._order_dict), len(self.horizontalHeaderLabelsList))

        self.table.setSortingEnabled(True)
        self.table.setHorizontalHeaderLabels(self.horizontalHeaderLabelsList)
        self.table.verticalHeader().hide()

        header = self.table.horizontalHeader()
        for i in range(len(self.horizontalHeaderLabelsList)):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        self.layout.addWidget(self.table)

    def add_order(self, order: AbstractExchangeHandler.OrderUpdate) -> str:
        order_id = order.client_orderID

        if order_id in self._order_dict.keys():
            self._edit_order(order)
        else:
            self.table.setSortingEnabled(False)

            self._order_dict[order_id] = order

            self.table.setRowCount(len(self._order_dict))

            for i, value in enumerate(dataclasses.asdict(order).values()):
                self.table.setItem(
                    len(self._order_dict) - 1, i, self.createItem(str(value))
                )

            self.table.setSortingEnabled(True)

            return order_id

    def _edit_order(self, order: AbstractExchangeHandler.OrderUpdate) -> str:
        self.table.setSortingEnabled(False)

        order_id = order.client_orderID
        order_index = list(self._order_dict.keys()).index(order_id)

        for i, value in enumerate(dataclasses.asdict(order).values()):
            self.table.item(order_index, i).setText(str(value))

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
