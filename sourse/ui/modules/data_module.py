from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from sourse.marketmaker import MarketMaker

from PyQt5 import QtCore, QtWidgets, QtGui


class DataModule(BaseUIModule):
    def _create_widgets(self):
        self.layout = QtWidgets.QVBoxLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Current Settings")
        self.base_widget.setLayout(self.layout)

        label = QtWidgets.QLabel("Your position: XBTUSD")
        font = label.font()
        font.setPointSize(14)
        label.setFont(font)
        label.setMargin(10)
        self.layout.addWidget(label)

        hbox = QtWidgets.QHBoxLayout()
        self.layout.addLayout(hbox)

        vbox_contracts = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox_contracts)
        vbox_contracts.setAlignment(QtCore.Qt.AlignCenter)
        self.volume_label = QtWidgets.QLabel("0")
        self.volume_label.setAlignment(QtCore.Qt.AlignCenter)
        vbox_contracts.addWidget(self.volume_label)

        vol_label_desc = QtWidgets.QLabel("Contracts")
        vol_label_desc.setAlignment(QtCore.Qt.AlignCenter)
        vbox_contracts.addWidget(vol_label_desc)
        vol_label_desc = QtWidgets.QLabel("Client")
        vol_label_desc.setAlignment(QtCore.Qt.AlignCenter)
        vbox_contracts.addWidget(vol_label_desc)

        vbox_contracts = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox_contracts)
        vbox_contracts.setAlignment(QtCore.Qt.AlignCenter)
        self.volume_label_server = QtWidgets.QLabel("0")
        self.volume_label_server.setAlignment(QtCore.Qt.AlignCenter)
        vbox_contracts.addWidget(self.volume_label_server)

        vol_label_desc = QtWidgets.QLabel("Contracts")
        vol_label_desc.setAlignment(QtCore.Qt.AlignCenter)
        vbox_contracts.addWidget(vol_label_desc)
        vol_label_desc = QtWidgets.QLabel("Server")
        vol_label_desc.setAlignment(QtCore.Qt.AlignCenter)
        vbox_contracts.addWidget(vol_label_desc)

        vbox_price = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox_price)
        vbox_price.setAlignment(QtCore.Qt.AlignCenter)
        self.price_label = QtWidgets.QLabel("-")
        self.price_label.setAlignment(QtCore.Qt.AlignCenter)
        vbox_price.addWidget(self.price_label)

        price_label_desc = QtWidgets.QLabel("Average price")
        vbox_price.addWidget(price_label_desc)
        price_label_desc.setAlignment(QtCore.Qt.AlignCenter)
        price_label_desc = QtWidgets.QLabel("Client")
        vbox_price.addWidget(price_label_desc)
        price_label_desc.setAlignment(QtCore.Qt.AlignCenter)

        vbox_price = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox_price)
        vbox_price.setAlignment(QtCore.Qt.AlignCenter)
        self.price_label_server = QtWidgets.QLabel("-")
        self.price_label_server.setAlignment(QtCore.Qt.AlignCenter)
        vbox_price.addWidget(self.price_label_server)

        price_label_desc = QtWidgets.QLabel("Average price")
        vbox_price.addWidget(price_label_desc)
        price_label_desc.setAlignment(QtCore.Qt.AlignCenter)
        price_label_desc = QtWidgets.QLabel("Server")
        vbox_price.addWidget(price_label_desc)
        price_label_desc.setAlignment(QtCore.Qt.AlignCenter)

        label = QtWidgets.QLabel("Your balance: XBTUSD")
        font = label.font()
        font.setPointSize(14)
        label.setFont(font)
        label.setMargin(10)
        self.layout.addWidget(label)

        hbox = QtWidgets.QHBoxLayout()
        self.layout.addLayout(hbox)
        vbox_contracts = QtWidgets.QVBoxLayout()
        vbox_price = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox_contracts)
        hbox.addLayout(vbox_price)
        vbox_contracts.setAlignment(QtCore.Qt.AlignCenter)
        vbox_price.setAlignment(QtCore.Qt.AlignCenter)

        self.rbalance_label = QtWidgets.QLabel("-")
        self.rbalance_label.setAlignment(QtCore.Qt.AlignCenter)
        vbox_contracts.addWidget(self.rbalance_label)

        vol_label_desc = QtWidgets.QLabel("Realised balance")
        vol_label_desc.setAlignment(QtCore.Qt.AlignCenter)
        vbox_contracts.addWidget(vol_label_desc)

        self.urprofit_label = QtWidgets.QLabel("-")
        self.urprofit_label.setAlignment(QtCore.Qt.AlignCenter)
        vbox_price.addWidget(self.urprofit_label)

        price_label_desc = QtWidgets.QLabel("Unrealised profit")
        vbox_price.addWidget(price_label_desc)
        price_label_desc.setAlignment(QtCore.Qt.AlignCenter)

        self.layout.addSpacerItem(
            QtWidgets.QSpacerItem(1, 1, vPolicy=QtWidgets.QSizePolicy.Expanding)
        )

        self._current_position_data: MarketMaker.Position = None

    @QtCore.pyqtSlot(object)
    def update_position(self, position: MarketMaker.Position):
        self._current_position_data = position
        self.price_label.setText(str(position.price) if position.volume != 0 else "-")
        self.volume_label.setText(str(position.volume))

    @QtCore.pyqtSlot(object)
    def update_position_server(self, position: MarketMaker.Position):
        # self._current_position_data = position
        self.price_label_server.setText(
            str(position.price) if position.price is not None else "-"
        )
        self.volume_label_server.setText(str(position.volume))

    @QtCore.pyqtSlot(float)
    def update_balance(self, balance: float):
        self.rbalance_label.setText(f"{round(balance, 8)} XBT")

    @QtCore.pyqtSlot(float)
    def update_price(self, price: float):
        if self._current_position_data is None:
            self.urprofit_label.setText("-")
        else:
            unr_profit = self._current_position_data.volume * (
                -1 / self._current_position_data.price + 1 / price
            )
            self.urprofit_label.setText(f"{round(unr_profit, 8)} XBT")
