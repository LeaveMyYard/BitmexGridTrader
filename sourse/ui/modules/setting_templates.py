from __future__ import annotations

from sourse.ui.modules.base_qdockwidget_module import BaseUIModule
from PyQt5 import QtWidgets, QtCore
from trade import MarketMaker
import typing
import json


class SettingTemplatesModule(BaseUIModule):
    template_selected = QtCore.pyqtSignal(str, object)

    def _create_widgets(self):
        layout = QtWidgets.QVBoxLayout(self.base_widget)
        self.parent_widget.setWindowTitle("Setting Templates")
        self.base_widget.setLayout(layout)

        self.scroll_box = QtWidgets.QScrollArea()
        layout.addWidget(self.scroll_box)

        self.layout = QtWidgets.QFormLayout(self.scroll_box)

        self.refresh_templates()

    def _clear_templates(self):
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
            load_button.pressed.connect(
                lambda name=name, template=settings: self.template_selected.emit(
                    name, template
                )
            )
            delete_button = QtWidgets.QPushButton("Delete")

            hlayout = QtWidgets.QHBoxLayout()
            hlayout.addWidget(load_button)
            hlayout.addWidget(delete_button)

            vlayout = QtWidgets.QVBoxLayout()
            vlayout.addLayout(hlayout)
            vlayout.addWidget(desc_label)
            self.layout.addRow(name_label, vlayout)

    @staticmethod
    def get_saved_templates(
        file: str = "./settings.json",
    ) -> typing.Iterator[typing.Tuple[str, str, MarketMaker.Settings]]:
        with open(file, mode="r") as settings_file:
            settings = json.load(settings_file)
            for template in settings["templates"]:
                name = template["name"]
                desc = template["desc"]

                del template["name"]
                del template["desc"]

                setting = MarketMaker.Settings(**template)
                yield (name, desc, setting)
