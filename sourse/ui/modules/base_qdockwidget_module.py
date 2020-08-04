import typing
from PyQt5 import QtWidgets, QtCore


class BaseUIModule(QtCore.QObject):
    def __init__(self, parent_widget: QtWidgets.QDockWidget):
        super().__init__(parent_widget)

        self.parent_widget = parent_widget
        self.base_widget = parent_widget.findChildren(QtWidgets.QWidget)[-1]
        self._create_widgets()

    def _create_widgets(self):
        raise NotImplementedError
