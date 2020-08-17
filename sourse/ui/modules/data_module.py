from sourse.ui.modules.base_qdockwidget_module import BaseUIModule

from PyQt5 import QtCore, QtWidgets


class DataModule(BaseUIModule):
    def _create_widgets(self):
        self.layout = QtWidgets.QVBoxLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Current Settings")
        self.base_widget.setLayout(self.layout)

        hbox = QtWidgets.QHBoxLayout()
        self.layout.addLayout(hbox)
        vbox_contracts = QtWidgets.QVBoxLayout()
        vbox_price = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox_contracts)
        hbox.addLayout(vbox_price)
        vbox_contracts.setAlignment(QtCore.Qt.AlignCenter)
        vbox_price.setAlignment(QtCore.Qt.AlignCenter)

        self.volume_label = QtWidgets.QLabel("0")
        self.volume_label.setAlignment(QtCore.Qt.AlignCenter)
        vbox_contracts.addWidget(self.volume_label)

        vol_label_desc = QtWidgets.QLabel("Contracts")
        vol_label_desc.setAlignment(QtCore.Qt.AlignCenter)
        vbox_contracts.addWidget(vol_label_desc)

        self.price_label = QtWidgets.QLabel("0.0")
        self.price_label.setAlignment(QtCore.Qt.AlignCenter)
        vbox_price.addWidget(self.price_label)

        price_label_desc = QtWidgets.QLabel("Average price")
        vbox_price.addWidget(price_label_desc)
        price_label_desc.setAlignment(QtCore.Qt.AlignCenter)
