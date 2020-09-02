from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from crypto_futures_py import AbstractExchangeHandler
import dataclasses
import typing
import numpy as np


class CurrentOrdersModule(BaseUIModule):
    order_canceled = QtCore.pyqtSignal(str)
    all_orders_canceled = QtCore.pyqtSignal()
    rebuild_grid = QtCore.pyqtSignal()

    def _create_widgets(self):
        self.layout = QtWidgets.QHBoxLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Orders")
        self.base_widget.setLayout(self.layout)

        self._order_dict: typing.Dict[
            str, typing.Tuple[int, AbstractExchangeHandler.OrderUpdate]
        ] = {}
        self._historical_order_dict: typing.Dict[
            str, typing.Tuple[int, AbstractExchangeHandler.OrderUpdate]
        ] = {}

        self.counter = 0
        self.historical_counter = 0

        self.horizontalHeaderLabelsList = [
            "Order id",  # 0
            "Client order id",  # 1
            "Status",  # 2
            "Symbol",  # 3
            "Price",  # 4
            "Average price",  # 5
            "Fee",  # 6
            "Fee asset",  # 7
            "Volume",  # 8
            "Volume realized",  # 9
            "Time",  # 10
            "id",  # 11
        ]

        self.colorfull_dictionary = {2: 2, 4: 8, 5: 8, 6: 6, 8: 8, 9: 9}

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
        header_historical.setSectionResizeMode(
            len(self.horizontalHeaderLabelsList) - 1,
            QtWidgets.QHeaderView.ResizeToContents,
        )

        self.menu = QtWidgets.QMenu()

        self.tabwidget = QtWidgets.QTabWidget()
        self.tabwidget.addTab(self.table, "Current orders")
        self.tabwidget.addTab(self.table_historical, "Historical orders")

        self.layout.addWidget(self.tabwidget)
        self.table.sortItems(
            len(self.horizontalHeaderLabelsList) - 1, QtCore.Qt.AscendingOrder
        )
        self.table_historical.sortItems(
            len(self.horizontalHeaderLabelsList) - 1, QtCore.Qt.AscendingOrder
        )

        self.table.setColumnHidden(len(self.horizontalHeaderLabelsList) - 1, True)
        self.table_historical.setColumnHidden(
            len(self.horizontalHeaderLabelsList) - 1, True
        )

        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.generateMenu)

        self.table.viewport().installEventFilter(self)

        self._stashed_orders: typing.List[
            typing.Tuple[AbstractExchangeHandler.OrderUpdate, bool]
        ] = []

        self._orders_to_delete: typing.Dict[str, datetime] = {}

        self.order_update_timer = QtCore.QTimer(self)
        self.order_update_timer.setInterval(200)
        self.order_update_timer.timeout.connect(self._update_orders_threadsafe)
        self.order_update_timer.start()

    def get_current_orders(self) -> typing.List[AbstractExchangeHandler.OrderUpdate]:
        return [v[1] for v in self._order_dict.values()]

    def get_historical_orders(self) -> typing.List[AbstractExchangeHandler.OrderUpdate]:
        return [v[1] for v in self._historical_order_dict.values()]

    def eventFilter(self, source, event):
        if (
            event.type() == QtCore.QEvent.MouseButtonPress
            and event.buttons() == QtCore.Qt.RightButton
        ):
            self._on_right_button_clicked(event)
            return True
        else:
            return False

    def _on_right_button_clicked(self, event):
        self.menu = QtWidgets.QMenu()

        item = self.table.itemAt(event.pos())
        if item is not None:
            if self.table.item(item.row(), 2).text() == "NEW":
                client_order_ID = self.table.item(item.row(), 1).text()
                self.menu.addAction(
                    "Cancel order", lambda: self.order_canceled.emit(client_order_ID),
                )

        self.menu.addAction(
            "Cancel all orders", lambda: self.all_orders_canceled.emit()
        )
        self.menu.addAction("Rebuild grid", lambda: self.rebuild_grid.emit())

    def generateMenu(self, pos):
        try:
            self.menu.exec_(self.table.mapToGlobal(pos))
        except:
            pass

    @QtCore.pyqtSlot()
    def _update_orders_threadsafe(self):
        for inp in self._stashed_orders.copy():
            self.add_order(*inp)
            self._stashed_orders.remove(inp)

        for order, time in self._orders_to_delete.copy().items():
            if order not in self._order_dict:
                del self._orders_to_delete[order]
            elif (datetime.now() - time).total_seconds() > 3:
                self.remove_order(order)
                del self._orders_to_delete[order]

    def add_order_threadsafe(
        self, order: AbstractExchangeHandler.OrderUpdate, historical_table: bool = False
    ):
        self._stashed_orders.append((order, historical_table))

    def add_order(
        self, order: AbstractExchangeHandler.OrderUpdate, historical_table: bool = False
    ) -> str:
        order_id = order.client_orderID if order.client_orderID != "" else order.orderID

        if order.status in ["FILLED", "CANCELED", "FAILED", "EXPIRED"]:
            self._orders_to_delete[order_id] = datetime.now()

        current_sorted_index = self.table.horizontalHeader().sortIndicatorSection()
        current_sorted_type = self.table.horizontalHeader().sortIndicatorOrder()
        self.table.sortItems(
            len(self.horizontalHeaderLabelsList) - 1, QtCore.Qt.AscendingOrder
        )
        self.table.setSortingEnabled(False)

        current_sorted_historical_index = (
            self.table_historical.horizontalHeader().sortIndicatorSection()
        )
        current_sorted_historical_type = (
            self.table_historical.horizontalHeader().sortIndicatorOrder()
        )
        self.table_historical.sortItems(10, QtCore.Qt.AscendingOrder)
        self.table_historical.setSortingEnabled(False)

        if not historical_table:
            if order_id in self._order_dict.keys():
                res = self._edit_order(order)
            elif order_id in self._historical_order_dict.keys():
                res = self.add_order(order, True)
            else:
                self._order_dict[order_id] = (len(self._order_dict), order)

                self.table.setRowCount(len(self._order_dict))

                for i, value in enumerate(dataclasses.asdict(order).values()):
                    color, value = self.highlight(i, order, value)

                    self.table.setItem(
                        len(self._order_dict) - 1, i, self.createItem(str(value), color)
                    )

                self.table.setItem(
                    len(self._order_dict) - 1,
                    len(self.horizontalHeaderLabelsList) - 1,
                    self.QTableWidgetIntegerItem(str(self.counter)),
                )
                self.counter += 1
                res = order_id
        else:
            if order_id in self._historical_order_dict.keys():
                res = self._edit_order(order, True)
            else:
                self._historical_order_dict[order_id] = (
                    len(self._historical_order_dict),
                    order,
                )

                self.table_historical.setRowCount(len(self._historical_order_dict))

                for i, value in enumerate(dataclasses.asdict(order).values()):
                    color, value = self.highlight(i, order, value)

                    self.table_historical.setItem(
                        len(self._historical_order_dict) - 1,
                        i,
                        self.createItem(str(value), color),
                    )

                self.table_historical.setItem(
                    len(self._historical_order_dict) - 1,
                    len(self.horizontalHeaderLabelsList) - 1,
                    self.QTableWidgetIntegerItem(str(self.historical_counter)),
                )
                self.historical_counter += 1
                res = order_id

        self.table.setSortingEnabled(True)
        self.table.sortItems(current_sorted_index, current_sorted_type)
        self.table_historical.setSortingEnabled(True)
        self.table_historical.sortItems(
            current_sorted_historical_index, current_sorted_historical_type
        )

        return res

    def _edit_order(
        self, order: AbstractExchangeHandler.OrderUpdate, historical_table: bool = False
    ) -> str:
        order_id = order.client_orderID if order.client_orderID != "" else order.orderID

        if historical_table:
            for i in range(self.table_historical.rowCount()):
                if str(order_id) == str(
                    self.table_historical.item(
                        i, 1 if order.client_orderID != "" else 0
                    ).text()
                ):
                    row = i
                    break
            else:
                raise ValueError(f"{order_id} not historical table")

            order_index = self._historical_order_dict[order_id][0]
            self._historical_order_dict[order_id] = order_index, order
        else:
            for i in range(self.table.rowCount()):
                if str(order_id) == str(
                    self.table.item(i, 1 if order.client_orderID != "" else 0).text()
                ):
                    row = i
                    break
            else:
                raise ValueError(f"{order_id} not historical table")

            order_index = self._order_dict[order_id][0]
            self._order_dict[order_id] = order_index, order

        for i, (key, value) in enumerate(dataclasses.asdict(order).items()):
            color, value = self.highlight(i, order, value)

            if key == "message":
                continue
            elif not historical_table:
                self.table.item(row, i).setText(str(value))
                self.table.item(row, i).setForeground(
                    QtGui.QBrush(QtGui.QColor(*color))
                )
            else:
                self.table_historical.item(row, i).setText(str(value))
                self.table_historical.item(row, i).setForeground(
                    QtGui.QBrush(QtGui.QColor(*color))
                )

        return order_id

    def highlight(
        self,
        i: int,
        order: AbstractExchangeHandler.OrderUpdate,
        value: typing.Union[int, float, str],
    ) -> typing.Tuple[typing.Tuple[int, int, int], typing.Union[int, float, str]]:
        if i in self.colorfull_dictionary.keys():
            j = list(dataclasses.asdict(order).values())[self.colorfull_dictionary[i]]
            try:
                if i == 5:
                    if float(j) < 0:
                        color = Colors.limegreen
                    elif float(j) > 0:
                        color = Colors.orangered
                    else:
                        color = Colors.yellow
                    value = np.format_float_positional(value)
                elif float(j) > 0:
                    color = Colors.limegreen
                elif float(j) < 0:
                    color = Colors.orangered
                else:
                    color = Colors.yellow
            except:
                color = (
                    Colors.limegreen
                    if str(j) == "FILLED"
                    else Colors.orangered
                    if str(j) == "CANCELED"
                    else Colors.yellow
                    if str(j) == "NEW"
                    else Colors.darkorange
                    if str(j) == "PENDING"
                    else Colors.white
                )
        else:
            color = Colors.white
        return color, value

    def remove_order(self, order_id) -> None:

        for i in range(self.table.rowCount()):
            if str(order_id) == str(self.table.item(i, 1).text()):
                row = i
                break
        else:
            raise ValueError(f"{order_id} not in 'Client order id' column")

        current_sorted_index = self.table.horizontalHeader().sortIndicatorSection()
        current_sorted_type = self.table.horizontalHeader().sortIndicatorOrder()
        self.table.sortItems(
            len(self.horizontalHeaderLabelsList) - 1, QtCore.Qt.AscendingOrder
        )
        self.table.setSortingEnabled(False)

        self.add_order(self._order_dict[order_id][1], True)
        self.table.removeRow(row)

        del self._order_dict[order_id]

        self.table.setSortingEnabled(True)
        self.table.sortItems(current_sorted_index, current_sorted_type)

    def remove_all_orders(self) -> None:
        self.table.setSortingEnabled(False)

        self._transfer_table()
        self._order_dict = {}
        self.table.setRowCount(0)

        self.table.setSortingEnabled(True)

    def _transfer_table(self) -> None:
        for i in self._order_dict:
            self.add_order(self._order_dict[i][1], True)

    class QTableWidgetIntegerItem(QtWidgets.QTableWidgetItem):
        def __lt__(self, other):
            try:
                return int(self.text()) < int(other.text())
            except ValueError:
                return self.text() < other.text()

    def createItem(
        self, text: str, color: typing.Tuple[int, int, int]
    ) -> QtWidgets.QTableWidgetItem:
        tableWidgetItem = QtWidgets.QTableWidgetItem(text)
        tableWidgetItem.setForeground(QtGui.QBrush(QtGui.QColor(*color)))
        tableWidgetItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        return tableWidgetItem


class Colors:
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

    white = (255, 255, 255)
    black = (0, 0, 0)

    yellow = (255, 255, 0)
    darkorange = (255, 140, 0)

    orangered = (255, 69, 0)
    limegreen = (50, 205, 50)

    neutralred = (239, 83, 80)
    neutralgreen = (38, 166, 154)

    def __init__(self):
        raise RuntimeError("Can not create an instance of a static Colors class")
