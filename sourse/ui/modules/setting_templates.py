from __future__ import annotations

from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from PyQt5 import QtWidgets, QtCore
from trade import MarketMaker
import typing
import json


class SettingTemplatesModule(BaseUIModule):
    template_selected = QtCore.pyqtSignal(str, object)

    def __init__(self, parent):
        self._load_buttons = []
        super().__init__(parent)

    def _create_widgets(self):
        layout = QtWidgets.QVBoxLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Setting Templates")
        self.base_widget.setLayout(layout)

        self.scroll_box = QtWidgets.QScrollArea()
        layout.addWidget(self.scroll_box)

        self.layout = QtWidgets.QFormLayout(self.scroll_box)

        self.refresh_templates()

    def _clear_templates(self):
        self._load_buttons = []
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if isinstance(item, QtWidgets.QWidgetItem):
                item.widget().deleteLater()
            elif isinstance(item, QtWidgets.QVBoxLayout):
                for j in reversed(range(item.count())):
                    item1 = item.itemAt(j)
                    if isinstance(item1, QtWidgets.QWidgetItem):
                        item1.widget().deleteLater()
                    elif isinstance(item1, QtWidgets.QHBoxLayout):
                        for k in reversed(range(item1.count())):
                            item1.itemAt(k).widget().deleteLater()

                item.setParent(None)

    @QtCore.pyqtSlot()
    def refresh_templates(self):
        self._clear_templates()
        for name, desc, settings in SettingTemplatesModule.get_saved_templates():
            name_label = QtWidgets.QLabel(f"{name} template:")
            desc_label = QtWidgets.QLabel(f"<i>{desc}</i><br>")
            desc_label.setWordWrap(True)
            load_button = QtWidgets.QPushButton("Load")
            self._load_buttons.append(load_button)
            load_button.pressed.connect(
                lambda name=name, template=settings: self.template_selected.emit(
                    name, template
                )
            )
            load_button.pressed.connect(
                lambda button=load_button: (
                    self.reset_load_buttons(),
                    button.setDisabled(True),
                )
            )
            delete_button = QtWidgets.QPushButton("Delete")

            @QtCore.pyqtSlot()
            def delete_template(template_name=name):
                settings = json.load(open("./settings.json", "r"))
                del settings["templates"][name]
                with open("./settings.json", "w") as f:
                    json.dump(settings, f)
                self.refresh_templates()

            delete_button.pressed.connect(delete_template)

            hlayout = QtWidgets.QHBoxLayout()
            hlayout.addWidget(load_button)
            hlayout.addWidget(delete_button)

            vlayout = QtWidgets.QVBoxLayout()
            vlayout.addLayout(hlayout)
            vlayout.addWidget(desc_label)
            self.layout.addRow(name_label, vlayout)

    @QtCore.pyqtSlot()
    def reset_load_buttons(self):
        for button in self._load_buttons:
            button.setEnabled(True)

    @staticmethod
    def get_saved_templates(
        file: str = "./settings.json",
    ) -> typing.Iterator[typing.Tuple[str, str, MarketMaker.Settings]]:
        with open(file, mode="r") as settings_file:
            settings = json.load(settings_file)
            for name, template in settings["templates"].items():
                desc = template["desc"]
                del template["desc"]

                setting = MarketMaker.Settings(**template)
                yield (name, desc, setting)
