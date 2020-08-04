from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from PyQt5 import QtWidgets, QtCore
from trade import MarketMaker
import typing


class CurrentSettingsModule(BaseUIModule):
    # A tuple of widget class and kwargs
    InputFormat = typing.Tuple[
        typing.Type[QtWidgets.QWidget], str, typing.Dict[str, typing.Tuple]
    ]

    def _create_widgets(self):
        self.layout = QtWidgets.QFormLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Current Settings")
        self.base_widget.setLayout(self.layout)

        settings_format: typing.Dict[str, CurrentSettingsModule.InputFormat] = {
            "Order pairs": (
                QtWidgets.QSpinBox,
                "Amount of orders on each side of the grid",
                {"setMinimum": (1,), "setMaximum": (100,), "setSuffix": (" pairs",)},
            ),
            "Order start size": (
                QtWidgets.QSpinBox,
                "The volume of the first order in each side of the grid (in contracts)",
                {
                    "setMinimum": (1,),
                    "setMaximum": (99999,),
                    "setSuffix": (" contracts",),
                },
            ),
            "Order step size": (
                QtWidgets.QSpinBox,
                "The amount of volume size, added to each next volume in a grid (in contracts)",
                {
                    "setMinimum": (0,),
                    "setMaximum": (99999,),
                    "setSuffix": (" contracts",),
                },
            ),
            "Interval": (
                QtWidgets.QDoubleSpinBox,
                "The distance between two consecutive orders on each size (in quote)",
                {
                    "setMinimum": (0.5,),
                    "setMaximum": (99999,),
                    "setDecimals": (1,),
                    "setSingleStep": (0.5,),
                },
            ),
            "Minimal spread": (
                QtWidgets.QDoubleSpinBox,
                "The distance between the first buy and the first sell order (in quote)",
                {
                    "setMinimum": (0.5,),
                    "setMaximum": (99999,),
                    "setDecimals": (1,),
                    "setSingleStep": (0.5,),
                },
            ),
            "Stop loss fund": (
                QtWidgets.QDoubleSpinBox,
                "The amount of bitcoins, that are allowed to loose per position.<br>The stop-loss order price is calculated.",
                {
                    "setMinimum": (0.0001,),
                    "setMaximum": (99999,),
                    "setDecimals": (4,),
                    "setSingleStep": (0.0001,),
                    "setSuffix": (" BTC",),
                },
            ),
            "Minimal position": (
                QtWidgets.QSpinBox,
                "The minimal size of the position (in contracts)",
                {
                    "setMinimum": (-1000000,),
                    "setMaximum": (0,),
                    "setSuffix": (" contracts",),
                },
            ),
            "Maximal position": (
                QtWidgets.QSpinBox,
                "The maximal size of the position (in contracts)",
                {
                    "setMinimum": (0,),
                    "setMaximum": (1000000,),
                    "setSuffix": (" contracts",),
                },
            ),
        }

        for name, value in settings_format.items():
            label = QtWidgets.QLabel(name + ":")
            widget = value[0](self.base_widget)

            for func_name, params in value[2].items():
                widget.__getattribute__(func_name)(*params)

            comment = QtWidgets.QLabel(f"<i>{value[1]}</i><br>")
            comment.setTextFormat(QtCore.Qt.RichText)

            vlayout = QtWidgets.QVBoxLayout()
            vlayout.addWidget(widget)
            vlayout.addWidget(comment)

            self.layout.addRow(label, vlayout)

        label = QtWidgets.QLabel("Save template:")
        hlayout = QtWidgets.QHBoxLayout()
        vlayout = QtWidgets.QVBoxLayout()
        name_input = QtWidgets.QLineEdit()
        desc_label = QtWidgets.QLabel(
            "<i>Save your current settings as a template.<br>\
            It will be saved in a file and could be loaded later.<br>\
            To change the saved template just save the settings with the same name.</i>"
        )
        save_button = QtWidgets.QPushButton("Save")
        save_button.setDisabled(True)

        hlayout.addWidget(name_input)
        hlayout.addWidget(save_button)

        vlayout.addLayout(hlayout)
        vlayout.addWidget(desc_label)

        name_input.textChanged.connect(lambda name: save_button.setEnabled(name != ""))

        self.layout.addRow(label, vlayout)

    @QtCore.pyqtSlot()
    def on_template_loaded(self, name: str, template: MarketMaker.Settings):
        print(name, template)
