from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from PyQt5 import QtWidgets, QtCore, QtGui
from sourse.exchange_handlers import AbstractExchangeHandler
import dataclasses
import typing
import numpy as np


class CurrentOrdersModule(BaseUIModule):
    def _create_widgets(self):
        """
        

        Returns
        -------
        None.

        """
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

        self.colorfull_dictionary = {2: 2, 3: 7, 4: 7, 5: 5, 7: 7, 8: 8}

        self.color = Colors()

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
            10, QtWidgets.QHeaderView.ResizeToContents
        )

        self.menu = QtWidgets.QMenu()

        self.tabwidget = QtWidgets.QTabWidget()
        self.tabwidget.addTab(self.table, "Current orders")
        self.tabwidget.addTab(self.table_historical, "Historical orders")

        self.layout.addWidget(self.tabwidget)
        self.table.sortItems(10, QtCore.Qt.AscendingOrder)
        self.table_historical.sortItems(10, QtCore.Qt.AscendingOrder)

        self.table.setColumnHidden(10, True)
        self.table_historical.setColumnHidden(10, True)

        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.generateMenu)

        self.table.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        if (
            event.type() == QtCore.QEvent.MouseButtonPress
            and event.buttons() == QtCore.Qt.RightButton
        ):
            self.on_right_button_clicked(event)
            return True
        else:
            return False

    def on_right_button_clicked(self, event):
        item = self.table.itemAt(event.pos())
        if item != None:
            tmp_client_order_ID = self.table.item(item.row(), 1).text()

            if item is not None and self.table.item(item.row(), 2).text() == "NEW":
                # TODO
                self.menu = QtWidgets.QMenu()
                self.menu.addAction("Cancel order")
            else:
                try:
                    del self.menu
                except:
                    pass

    def generateMenu(self, pos):
        try:
            self.menu.exec_(self.table.mapToGlobal(pos))
        except:
            pass

    def add_order(
        self, order: AbstractExchangeHandler.OrderUpdate, historical_table: bool = False
    ) -> str:
        """
        

        Parameters
        ----------
        order : AbstractExchangeHandler.OrderUpdate
            DESCRIPTION.
        historical_table : bool, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        str
            DESCRIPTION.

        """
        order_id = order.client_orderID if order.client_orderID != "" else order.orderID

        current_sorted_index = self.table.horizontalHeader().sortIndicatorSection()
        current_sorted_type = self.table.horizontalHeader().sortIndicatorOrder()
        self.table.sortItems(10, QtCore.Qt.AscendingOrder)
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
                    10,
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
                    10,
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
        """
        

        Parameters
        ----------
        order : AbstractExchangeHandler.OrderUpdate
            DESCRIPTION.
        historical_table : bool, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        str
            DESCRIPTION.

        """
        order_id = order.client_orderID if order.client_orderID != "" else order.orderID

        if historical_table:
            order_index = self._historical_order_dict[order_id][0]
            self._historical_order_dict[order_id] = order_index, order
        else:
            order_index = self._order_dict[order_id][0]
            self._order_dict[order_id] = order_index, order

        for i, (key, value) in enumerate(dataclasses.asdict(order).items()):
            color, value = self.highlight(i, order, value)

            if key == "message":
                continue
            elif not historical_table:
                self.table.item(order_index, i).setText(str(value))
                self.table.item(order_index, i).setForeground(
                    QtGui.QBrush(QtGui.QColor(*color))
                )
            else:
                self.table_historical.item(order_index, i).setText(str(value))
                self.table_historical.item(order_index, i).setForeground(
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
                        color = self.color.limegreen
                    elif float(j) > 0:
                        color = self.color.orangered
                    else:
                        color = self.color.yellow
                    value = np.format_float_positional(value)
                elif float(j) > 0:
                    color = self.color.limegreen
                elif float(j) < 0:
                    color = self.color.orangered
                else:
                    color = self.color.yellow
            except:
                color = (
                    self.color.limegreen
                    if str(j) == "FILLED"
                    else self.color.orangered
                    if str(j) == "CANCELED"
                    else self.color.yellow
                    if str(j) == "NEW"
                    else self.color.darkorange
                    if str(j) == "PENDING"
                    else self.color.white
                )
        else:
            color = self.color.white
        return color, value

    def remove_all_orders(self) -> None:
        """
        

        Returns
        -------
        None
            DESCRIPTION.

        """
        self.table.setSortingEnabled(False)

        self._transfer_table()
        self._order_dict = {}
        self.table.setRowCount(0)

        self.table.setSortingEnabled(True)

    def _transfer_table(self) -> None:
        """
        

        Returns
        -------
        None
            DESCRIPTION.

        """
        for i in self._order_dict:
            self.add_order(self._order_dict[i][1], True)

    class QTableWidgetIntegerItem(QtWidgets.QTableWidgetItem):
        def __lt__(self, other):
            """
            

            Parameters
            ----------
            other : TYPE
                DESCRIPTION.

            Returns
            -------
            TYPE
                DESCRIPTION.

            """
            return int(self.text()) < int(other.text())

    def createItem(
        self, text: str, color: typing.Tuple[int, int, int]
    ) -> QtWidgets.QTableWidgetItem:
        """
        

        Parameters
        ----------
        text : str
            DESCRIPTION.
        color : typing.Tuple[int, int, int]
            DESCRIPTION.

        Returns
        -------
        tableWidgetItem : TYPE
            DESCRIPTION.

        """
        tableWidgetItem = QtWidgets.QTableWidgetItem(text)
        tableWidgetItem.setForeground(QtGui.QBrush(QtGui.QColor(*color)))
        tableWidgetItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        return tableWidgetItem


class Colors:
    def __init__(self):
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)

        self.white = (255, 255, 255)
        self.black = (0, 0, 0)

        self.yellow = (255, 255, 0)
        self.darkorange = (255, 140, 0)

        self.orangered = (255, 69, 0)
        self.limegreen = (50, 205, 50)

        self.neutralred = (239, 83, 80)
        self.neutralgreen = (38, 166, 154)

