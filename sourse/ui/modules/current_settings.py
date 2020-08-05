from __future__ import annotations

from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from PyQt5 import QtWidgets, QtCore
from trade import MarketMaker
import typing
import json


class InputFormat:
    def __init__(
        self,
        widget_type: typing.Type[QtWidgets.QWidget],
        name: str,
        desc: str,
        params: typing.Dict[str, typing.Tuple],
    ):
        self.widget_type = widget_type
        self.name = name
        self.desc = desc
        self.params = params


class CurrentSettingsModule(BaseUIModule):
    templates_updated = QtCore.pyqtSignal()
    settings_changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        self._setting_widgets: typing.Dict[str, QtWidgets.QWidget] = {}
        super().__init__(parent)

    @staticmethod
    def _get_settings_description() -> typing.Dict[str, InputFormat]:
        d: typing.Dict[str, InputFormat] = {}

        settings_data = json.load(open("settings.json", "r"))["settings_description"]
        for i in MarketMaker.Settings.__dataclass_fields__.keys():
            data = settings_data[i]
            name = data["name"]
            desc = data["desc"]
            type_data = data["type_data"]

            params: typing.Dict[str, typing.Tuple] = {}

            if type_data["type"] == "int":
                widget = QtWidgets.QSpinBox
                params["setMinimum"] = (type_data["minimum"],)
                params["setMaximum"] = (type_data["maximum"],)
                if "suffix" in type_data:
                    params["setSuffix"] = (type_data["suffix"],)

            elif type_data["type"] == "float":
                widget = QtWidgets.QDoubleSpinBox
                params["setMinimum"] = (type_data["minimum"],)
                params["setMaximum"] = (type_data["maximum"],)
                params["setDecimals"] = (type_data["decimals"],)
                params["setSingleStep"] = (type_data["step"],)
                if "suffix" in type_data:
                    params["setSuffix"] = (type_data["suffix"],)

            else:
                raise ValueError

            d[i] = InputFormat(widget, name, desc, params)

        return d

    def _create_widgets(self):
        self.layout = QtWidgets.QVBoxLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Current Settings")
        self.base_widget.setLayout(self.layout)

        self.layout.addWidget(self._create_keys_groupbox())
        self.layout.addWidget(self._create_algorithm_groupbox())
        self.layout.addWidget(self._create_template_saving_groupbox())

        for i, v in enumerate([0, 1, 0]):
            self.layout.setStretch(i, v)

    def _create_keys_groupbox(self) -> QtWidgets.QGroupBox:
        group_box = QtWidgets.QGroupBox("Keys")
        layout = QtWidgets.QFormLayout(group_box)

        settings_data = json.load(open("settings.json", "r"))["bitmex_client"]

        label = QtWidgets.QLabel("Public key:")
        widget = QtWidgets.QLineEdit()
        widget.setText(settings_data["public_key"])
        layout.addRow(label, widget)

        label = QtWidgets.QLabel("Private key:")
        widget = QtWidgets.QLineEdit()
        widget.setText(settings_data["private_key"])
        layout.addRow(label, widget)

        return group_box

    def _create_algorithm_groupbox(self) -> QtWidgets.QGroupBox:
        group_box = QtWidgets.QGroupBox("Algorithm")
        layout = QtWidgets.QFormLayout(group_box)

        settings_format: typing.Dict[
            str, InputFormat
        ] = self._get_settings_description()

        for name, value in settings_format.items():
            label = QtWidgets.QLabel(value.name + ":")
            widget = value.widget_type(group_box)

            widget.valueChanged.connect(self.settings_changed)

            self._setting_widgets[name] = widget

            for func_name, params in value.params.items():
                widget.__getattribute__(func_name)(*params)

            comment = QtWidgets.QLabel(f"<i>{value.desc}</i><br>")
            comment.setTextFormat(QtCore.Qt.RichText)
            comment.setWordWrap(True)

            vlayout = QtWidgets.QVBoxLayout()
            vlayout.addWidget(widget)
            vlayout.addWidget(comment)

            layout.addRow(label, vlayout)

        return group_box

    def _create_template_saving_groupbox(self) -> QtWidgets.QGroupBox:
        group_box = QtWidgets.QGroupBox("Save template")
        outer_vlayout = QtWidgets.QVBoxLayout(group_box)
        layout = QtWidgets.QFormLayout()
        outer_vlayout.addLayout(layout)

        label = QtWidgets.QLabel("Template name:")
        vlayout = QtWidgets.QVBoxLayout()
        name_input = QtWidgets.QLineEdit()
        name_label = QtWidgets.QLabel("<i>The name of your template</i><br>")
        name_label.setWordWrap(True)
        vlayout.addWidget(name_input)
        vlayout.addWidget(name_label)
        layout.addRow(label, vlayout)

        label = QtWidgets.QLabel("Template description:")
        vlayout = QtWidgets.QVBoxLayout()
        desc_input = QtWidgets.QLineEdit()
        desc_label = QtWidgets.QLabel("<i>The description of your template</i><br>")
        desc_label.setWordWrap(True)
        vlayout.addWidget(desc_input)
        vlayout.addWidget(desc_label)
        layout.addRow(label, vlayout)

        save_button = QtWidgets.QPushButton("Save")
        save_button.setDisabled(True)

        outer_vlayout.addWidget(save_button)

        name_input.textChanged.connect(
            lambda name: save_button.setEnabled(name != "" and desc_input.text() != "")
        )
        desc_input.textChanged.connect(
            lambda name: save_button.setEnabled(name != "" and name_input.text() != "")
        )

        @QtCore.pyqtSlot()
        def save_template():
            name = name_input.text()
            desc = desc_input.text()

            settings = json.load(open("./settings.json", "r"))

            settings["templates"][name] = dict(
                desc=desc,
                **{
                    name: widget.value()
                    for name, widget in self._setting_widgets.items()
                },
            )

            with open("./settings.json", "w") as f:
                json.dump(settings, f)

            self.templates_updated.emit()

        save_button.pressed.connect(save_template)

        return group_box

    @QtCore.pyqtSlot()
    def on_template_loaded(self, name: str, template: MarketMaker.Settings):
        for setting_name in self._setting_widgets:
            self._setting_widgets[setting_name].setValue(
                template.__getattribute__(setting_name)
            )

    def get_current_settings(self) -> MarketMaker.Settings:
        return MarketMaker.Settings(
            **{name: widget.value() for name, widget in self._setting_widgets.items()}
        )

