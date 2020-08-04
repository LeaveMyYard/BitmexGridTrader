from sourse.ui.modules.base_qdockwidget_module import IQDockWidgetModule
from PyQt5 import QtWidgets
import typing


class CurrentSettingsModule(IQDockWidgetModule):

    # A tuple of widget class and kwargs
    InputFormat = typing.Tuple[
        typing.Type[QtWidgets.QWidget], typing.Dict[str, typing.Any]
    ]

    def _create_widgets(self):
        self.layout = QtWidgets.QFormLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Current Settings")
        self.base_widget.setLayout(self.layout)

        settings_format: typing.Dict[str, CurrentSettingsModule.InputFormat] = {
            "Order pairs": (QtWidgets.QSpinBox, {}),
            "Order start size": (QtWidgets.QSpinBox, {}),
            "Order step size": (QtWidgets.QSpinBox, {}),
            "Interval": (QtWidgets.QSpinBox, {}),
            "Minimal spread": (QtWidgets.QSpinBox, {}),
            "Stop loss fund": (QtWidgets.QSpinBox, {}),
            "Minimal position": (QtWidgets.QSpinBox, {}),
            "Maximal position": (QtWidgets.QSpinBox, {}),
        }

        for name, value in settings_format.items():
            label = QtWidgets.QLabel(name + ":")
            widget = value[0](**value[1])

            self.layout.addRow(label, widget)
