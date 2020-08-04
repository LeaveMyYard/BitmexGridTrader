import abc
import typing
from PyQt5 import QtWidgets


class BaseUIModule(metaclass=abc.ABCMeta):
    def __init__(self, parent_widget: QtWidgets.QDockWidget):
        self.parent_widget = parent_widget
        self.base_widget = parent_widget.findChildren(QtWidgets.QWidget)[-1]
        self._create_widgets()

    @abc.abstractmethod
    def _create_widgets(self):
        ...
