from __future__ import annotations

from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from PyQt5 import QtWidgets, QtCore
from sourse.marketmaker import MarketMaker
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
    start_button_pressed = QtCore.pyqtSignal()
    stop_button_pressed = QtCore.pyqtSignal()

    cancel_all_orders = QtCore.pyqtSignal()
    fill_position = QtCore.pyqtSignal()

    def __init__(
        self,
        parent,
        marketmaker_finished_predicate: typing.Callable[[], typing.Tuple[bool, bool]],
    ):
        self._setting_widgets: typing.Dict[str, QtWidgets.QWidget] = {}
        self._keys_widgets: typing.Dict[str, typing.Optional[QtWidgets.QtWidget]] = {
            "private": None,
            "public": None,
        }
        self._marketmaker_finished_predicate = marketmaker_finished_predicate
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

            elif type_data["type"] == "bool":
                widget = QtWidgets.QCheckBox

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

        self.layout.addWidget(self._create_start_stop_button())

        for i, v in enumerate([0, 1, 0]):
            self.layout.setStretch(i, v)

    def _create_start_stop_button(self) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton("Start bot")
        running: bool = False

        @QtCore.pyqtSlot()
        def on_pressed():
            nonlocal running

            if running:
                (
                    position_filled,
                    orders_canceled,
                ) = self._marketmaker_finished_predicate()

                if not position_filled or not orders_canceled:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Question)
                    msg.setWindowTitle("The bot is unfinished")
                    msg.setText("The bot work in unfinished, choose what to do")
                    stop_button = msg.addButton(
                        "Just stop", QtWidgets.QMessageBox.AcceptRole
                    )

                    cancel_orders = None
                    fill_position = None
                    both_actions = None

                    if not position_filled and not orders_canceled:
                        msg.setInformativeText(
                            f"Right now it seems that there are some opened orders and unrealised position."
                        )
                        cancel_orders = msg.addButton(
                            "Cancel orders", QtWidgets.QMessageBox.AcceptRole,
                        )
                        fill_position = msg.addButton(
                            "Fill position", QtWidgets.QMessageBox.AcceptRole,
                        )
                        both_actions = msg.addButton(
                            "Do both", QtWidgets.QMessageBox.AcceptRole,
                        )

                    elif not position_filled:
                        msg.setInformativeText(
                            f"Right now it seems that there is unrealised position."
                        )
                        fill_position = msg.addButton(
                            "Fill position", QtWidgets.QMessageBox.AcceptRole,
                        )
                    elif not orders_canceled:
                        msg.setInformativeText(
                            f"Right now it seems that there are some opened orders."
                        )
                        cancel_orders = msg.addButton(
                            "Cancel orders", QtWidgets.QMessageBox.AcceptRole,
                        )

                    cancel_button = msg.addButton(
                        "Cancel", QtWidgets.QMessageBox.RejectRole
                    )
                    msg.exec()

                    if msg.clickedButton() == cancel_button:
                        return
                    elif msg.clickedButton() == cancel_orders:
                        self.cancel_all_orders.emit()
                    elif msg.clickedButton() == fill_position:
                        self.fill_position.emit()
                    elif msg.clickedButton() == both_actions:
                        self.cancel_all_orders.emit()
                        self.fill_position.emit()

                button.setText("Start bot")
                self.stop_button_pressed.emit()
            else:
                button.setText("Stop bot")
                self.start_button_pressed.emit()

            running = not running

        button.pressed.connect(on_pressed)

        return button

    def _create_keys_groupbox(self) -> QtWidgets.QGroupBox:
        group_box = QtWidgets.QGroupBox("Keys")
        layout = QtWidgets.QFormLayout(group_box)

        settings_data = json.load(open("settings.json", "r"))["bitmex_client"]

        label = QtWidgets.QLabel("Public key:")
        widget = QtWidgets.QLineEdit()
        widget.setText(settings_data["public_key"])
        layout.addRow(label, widget)
        self._keys_widgets["public"] = widget

        label = QtWidgets.QLabel("Private key:")
        widget = QtWidgets.QLineEdit()
        widget.setText(settings_data["private_key"])
        layout.addRow(label, widget)
        self._keys_widgets["private"] = widget

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

            if value.widget_type is QtWidgets.QCheckBox:
                widget.stateChanged.connect(self.settings_changed)
            else:
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

            if name in settings["templates"]:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Question)
                # msg.setIconPixmap(pixmap)  # Своя картинка

                msg.setWindowTitle("Template already exists")
                msg.setText(f'Template called "{name}" already exists.')
                msg.setInformativeText(
                    "The template, you wanted to create already exists. Do you want to replace it?"
                )

                okButton = msg.addButton("Yes", QtWidgets.QMessageBox.AcceptRole)
                msg.addButton("No", QtWidgets.QMessageBox.RejectRole)

                msg.exec()
                if msg.clickedButton() != okButton:
                    return

            settings["templates"][name] = dict(
                desc=desc,
                **{
                    name: (
                        widget.value()
                        if widget.__class__ is not QtWidgets.QCheckBox
                        else widget.checkState() == QtCore.Qt.Checked
                    )
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
            if self._setting_widgets[setting_name].__class__ is QtWidgets.QCheckBox:
                self._setting_widgets[setting_name].setCheckState(
                    QtCore.Qt.Checked
                    if template.__getattribute__(setting_name)
                    else QtCore.Qt.Unchecked
                )
            else:
                self._setting_widgets[setting_name].setValue(
                    template.__getattribute__(setting_name)
                )

    def get_current_settings(self) -> MarketMaker.Settings:
        return MarketMaker.Settings(
            **{
                name: (
                    widget.value()
                    if widget.__class__ is not QtWidgets.QCheckBox
                    else widget.checkState() == QtCore.Qt.Checked
                )
                for name, widget in self._setting_widgets.items()
            }
        )

    def get_current_keys(self) -> typing.Tuple[str, str]:
        if (
            self._keys_widgets["public"] is not None
            and self._keys_widgets["private"] is not None
        ):
            return (
                self._keys_widgets["public"].text(),
                self._keys_widgets["private"].text(),
            )

        raise RuntimeError

