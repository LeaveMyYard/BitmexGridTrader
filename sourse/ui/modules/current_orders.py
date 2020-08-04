from sourse.ui.modules.base_qdockwidget_module import IQDockWidgetModule
from PyQt5 import QtWidgets
import typing


class CurrentOrdersModule(IQDockWidgetModule):
    def _create_widgets(self):
        self.layout = QtWidgets.QFormLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Current Orders")
        self.base_widget.setLayout(self.layout)

        ...

    def add_order(self, price: float, volume: float) -> int:
        ...

    def remove_order(self, order_id: int) -> None:
        ...
