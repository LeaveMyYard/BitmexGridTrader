from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from sourse.marketmaker import MarketMaker

from PyQt5 import QtCore, QtWidgets, QtGui


def set_label_font_size(label: QtWidgets.QLabel, size: int) -> None:
    font = label.font()
    font.setPointSize(size)
    label.setFont(font)


class DataDisplayWidget(QtWidgets.QWidget):
    smaller_text_size = 7

    def __init__(
        self, text: str, subtext: str, default: str = "", parent: QtCore.QObject = None,
    ):
        super().__init__(parent)

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)
        vbox.setAlignment(QtCore.Qt.AlignCenter)
        self.data_label = QtWidgets.QLabel(default)
        self.data_label.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(self.data_label)

        desc_label = QtWidgets.QLabel(text)
        desc_label.setMargin(-2)
        desc_label.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(desc_label)

        desc_label = QtWidgets.QLabel(subtext)
        desc_label.setMargin(-2)
        set_label_font_size(desc_label, self.smaller_text_size)
        desc_label.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(desc_label)

    def setText(self, text: str) -> None:
        self.data_label.setText(text)


class DataModule(BaseUIModule):
    def _create_widgets(self):
        self.layout = QtWidgets.QVBoxLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Current Settings")
        self.base_widget.setLayout(self.layout)

        bigger_text_size = 14

        label = QtWidgets.QLabel("Your position: XBTUSD")
        set_label_font_size(label, bigger_text_size)
        label.setMargin(10)
        self.layout.addWidget(label)

        hbox = QtWidgets.QHBoxLayout()
        self.layout.addLayout(hbox)

        # ----- Client Contracts -----
        self.client_contracts = DataDisplayWidget("Contracts", "Client", default="0")
        hbox.addWidget(self.client_contracts)

        # ----- Server Contracts -----
        self.server_contracts = DataDisplayWidget("Contracts", "Server", default="0")
        hbox.addWidget(self.server_contracts)

        # ----- Client Average Price -----
        self.client_price = DataDisplayWidget("Average price", "Client", default="-")
        hbox.addWidget(self.client_price)

        # ----- Server Average Price -----
        self.server_price = DataDisplayWidget("Average Price", "Server", default="-")
        hbox.addWidget(self.server_price)

        label = QtWidgets.QLabel("Your balance: XBTUSD")
        set_label_font_size(label, bigger_text_size)
        label.setMargin(10)
        self.layout.addWidget(label)

        hbox = QtWidgets.QHBoxLayout()
        self.layout.addLayout(hbox)

        # ----- Client Balance -----
        self.client_balance = DataDisplayWidget("Balance", "Client", default="0 XBT")
        hbox.addWidget(self.client_balance)

        # ----- Server Balance -----
        self.server_balance = DataDisplayWidget("Balance", "Server", default="0 XBT")
        hbox.addWidget(self.server_balance)

        # ----- Unr.Profit Client -----
        self.client_profit = DataDisplayWidget("Unr. Profit", "Client", default="0")
        hbox.addWidget(self.client_profit)

        # ----- Unr.Profit Server -----
        self.server_profit = DataDisplayWidget("Unr. Profit", "Server", default="0")
        hbox.addWidget(self.server_profit)

        self.layout.addSpacerItem(
            QtWidgets.QSpacerItem(1, 1, vPolicy=QtWidgets.QSizePolicy.Expanding)
        )

        self._current_server_position_data: MarketMaker.Position = None
        self._current_client_position_data: MarketMaker.Position = None

    @QtCore.pyqtSlot(object)
    def update_position(self, position: MarketMaker.Position):
        self._current_client_position_data = position
        self.client_price.setText(str(position.price) if position.volume != 0 else "-")
        self.client_contracts.setText(str(position.volume))

    @QtCore.pyqtSlot(object)
    def update_position_server(self, position: MarketMaker.Position):
        self._current_server_position_data = position
        self.server_price.setText(
            str(position.price) if position.price is not None else "-"
        )
        self.server_contracts.setText(str(position.volume))

    @QtCore.pyqtSlot(float)
    def update_balance(self, balance: float):
        self.client_balance.setText(f"{round(balance, 8)} XBT")

    @QtCore.pyqtSlot(float)
    def update_balance_server(self, balance: float):
        self.server_balance.setText(f"{round(balance, 8)} XBT")

    @QtCore.pyqtSlot(float)
    def update_price(self, price: float):
        if self._current_client_position_data is None:
            self.client_profit.setText("-")
        else:
            unr_profit = self._current_client_position_data.volume * (
                -1 / self._current_client_position_data.price + 1 / price
            )
            self.client_profit.setText(f"{round(unr_profit, 8)} XBT")

        if self._current_server_position_data is None:
            self.server_profit.setText("-")
        else:
            unr_profit = self._current_server_position_data.volume * (
                -1 / self._current_server_position_data.price + 1 / price
            )
            self.server_profit.setText(f"{round(unr_profit, 8)} XBT")
