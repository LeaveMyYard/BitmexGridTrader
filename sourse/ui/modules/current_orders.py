from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from PyQt5 import QtWidgets, QtCore
from sourse.exchange_handlers import AbstractExchangeHandler
import datetime
import dataclasses
import typing


class CurrentOrdersModule(BaseUIModule):
    def _create_widgets(self):
        self.layout = QtWidgets.QHBoxLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Orders")
        self.base_widget.setLayout(self.layout)

        self._order_dict = {}
        self._historical_order_dict = {}

        self.counter = 0
        self.historical_counter = 0

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
            "id",
        ]

        self.table = QtWidgets.QTableWidget(
            len(self._order_dict), len(self.horizontalHeaderLabelsList)
        )
        self.table_historical = QtWidgets.QTableWidget(
            len(self._order_dict), len(self.horizontalHeaderLabelsList)
        )

        self.table.setSortingEnabled(True)
        self.table_historical.setSortingEnabled(True)
        self.table.setHorizontalHeaderLabels(self.horizontalHeaderLabelsList)
        self.table_historical.setHorizontalHeaderLabels(self.horizontalHeaderLabelsList)
        self.table.verticalHeader().hide()
        self.table_historical.verticalHeader().hide()

        header = self.table.horizontalHeader()
        header_historical = self.table_historical.horizontalHeader()
        for i in range(len(self.horizontalHeaderLabelsList)):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
            header_historical.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        self.tabwidget = QtWidgets.QTabWidget()
        self.tabwidget.addTab(self.table, "Current orders")
        self.tabwidget.addTab(self.table_historical, "Historical orders")

        self.layout.addWidget(self.tabwidget)
        self.table.sortItems(10, QtCore.Qt.AscendingOrder)

        self.table.setColumnHidden(10, True)

    def add_order(self, order: AbstractExchangeHandler.OrderUpdate) -> str:
        order_id = order.client_orderID

        current_sorted_index = self.table.horizontalHeader().sortIndicatorSection()
        current_sorted_type = self.table.horizontalHeader().sortIndicatorOrder()
        self.table.sortItems(10, QtCore.Qt.AscendingOrder)
        self.table.setSortingEnabled(False)

        if order_id in self._order_dict.keys():
            res = self._edit_order(order)
        elif order_id in self._historical_order_dict.keys():
            res = self.add_order_to_historical(order)
        else:
            self._order_dict[order_id] = (len(self._order_dict), order)

            self.table.setRowCount(len(self._order_dict))

            for i, value in enumerate(dataclasses.asdict(order).values()):
                self.table.setItem(
                    len(self._order_dict) - 1, i, self.createItem(str(value))
                )

            self.table.setItem(
                len(self._order_dict) - 1,
                10,
                self.QTableWidgetIntegerItem(str(self.counter)),
            )
            self.counter += 1
            res = order_id

        self.table.setSortingEnabled(True)
        self.table.sortItems(current_sorted_index, current_sorted_type)

        return res

    def add_order_to_historical(
        self, order: AbstractExchangeHandler.OrderUpdate
    ) -> str:
        order_id = order.client_orderID

        current_sorted_index = (
            self.table_historical.horizontalHeader().sortIndicatorSection()
        )
        current_sorted_type = (
            self.table_historical.horizontalHeader().sortIndicatorOrder()
        )
        self.table_historical.sortItems(10, QtCore.Qt.AscendingOrder)
        self.table_historical.setSortingEnabled(False)

        # self._historical_order_dict[order_id] = (len(self._historical_order_dict), order)

        if order_id in self._historical_order_dict.keys():
            self._edit_historical_order(order)
        else:
            self.table_historical.setRowCount(len(self._historical_order_dict))

            for i, value in enumerate(dataclasses.asdict(order).values()):
                self.table_historical.setItem(
                    len(self._historical_order_dict) - 1, i, self.createItem(str(value))
                )

            self.table_historical.setItem(
                len(self._historical_order_dict) - 1,
                10,
                self.QTableWidgetIntegerItem(str(self.historical_counter)),
            )
            self.historical_counter += 1
            res = order_id

        self.table_historical.setSortingEnabled(True)
        self.table_historical.sortItems(current_sorted_index, current_sorted_type)

        return res

    def _edit_order(self, order: AbstractExchangeHandler.OrderUpdate) -> str:
        order_id = order.client_orderID
        order_index = self._order_dict[order_id][0]

        for i, (key, value) in enumerate(dataclasses.asdict(order).items()):
            if key == "message":
                continue
            self.table.item(order_index, i).setText(str(value))

        return order_id

    def _edit_historical_order(self, order: AbstractExchangeHandler.OrderUpdate) -> str:
        order_id = order.client_orderID
        order_index = self._historical_order_dict[order_id][0]

        for i, (key, value) in enumerate(dataclasses.asdict(order).items()):
            if key == "message":
                continue
            self.table_historical.item(order_index, i).setText(str(value))

        return order_id

    def remove_order(self, order_id: int) -> None:
        # TODO
        self.table.setSortingEnabled(False)

        del self._order_dict[order_id]
        self.table.removeRow(list(self._order_dict.keys()).index(order_id))

        self.table.setSortingEnabled(True)

    def remove_all_orders(self) -> None:
        self.table.setSortingEnabled(False)

        self._transfer_table()
        self._order_dict = {}
        self.table.setRowCount(0)

        self.table.setSortingEnabled(True)

    def _transfer_table(self) -> None:
        for i in self._order_dict:
            self.add_order_to_historical(self._order_dict[i][1])
            self._historical_order_dict[i] = (
                len(self._historical_order_dict),
                self._order_dict[i][1],
            )

    class QTableWidgetIntegerItem(QtWidgets.QTableWidgetItem):
        def __lt__(self, other):
            return int(self.text()) < int(other.text())

    @staticmethod
    def createItem(text: str) -> QtWidgets.QTableWidgetItem:
        tableWidgetItem = QtWidgets.QTableWidgetItem(text)
        tableWidgetItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        return tableWidgetItem
