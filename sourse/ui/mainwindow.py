from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sourse.ui.modules as UiModules
import asyncio
import quamash
import threading
from sourse.marketmaker import MarketMaker
from sourse.exchange_handlers import BitmexExchangeHandler
import typing


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("sourse/ui/mainwindow.ui", self)  # Load the .ui file
        # # self.setWindowIcon(QtGui.QIcon("assets/icon_1.png"))

        self.top_left_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget"
        )
        self.bottom_left_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget_2"
        )
        self.top_right_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget_3"
        )
        self.bottom_right_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget_4"
        )
        self.bottom_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget_5"
        )

        self.current_settings = UiModules.CurrentSettingsModule(
            self.top_right_dockwidget
        )

        self.setting_templates = UiModules.SettingTemplatesModule(
            self.bottom_right_dockwidget
        )

        self.setting_templates.template_selected.connect(
            lambda name, settings: self.current_settings.on_template_loaded(
                name, settings
            )
        )
        self.current_settings.templates_updated.connect(
            self.setting_templates.refresh_templates
        )
        self.current_settings.settings_changed.connect(
            self.setting_templates.reset_load_buttons
        )
        self.current_settings.start_button_pressed.connect(self.start)

        self.current_orders = UiModules.CurrentOrdersModule(self.bottom_dockwidget)

        self.chart = UiModules.Chart(self)

        self.handle = BitmexExchangeHandler(*self.current_settings.get_current_keys())
        self.handle.start_kline_socket_threaded(
            self._on_kline_event_appeared, "1m", "XBTUSD"
        )

        self.marketmaker: MarketMaker = None
        self.worker_thread: QtCore.QThread = None

        self.show()

    class Worker(QtCore.QThread):
        def run(self, mainwindow):
            handler = BitmexExchangeHandler(
                *mainwindow.current_settings.get_current_keys()
            )
            mainwindow.marketmaker = MarketMaker(
                "XBTUSD", handler, mainwindow.current_settings.get_current_settings()
            )

            mainwindow.marketmaker.candle_appeared.connect(
                lambda x: mainwindow._on_kline_event_appeared(x)
            )

            loop = quamash.QEventLoop(QtCore.QCoreApplication.instance())
            asyncio.set_event_loop(loop)

            with loop:
                loop.run_until_complete(mainwindow.marketmaker.start())

    @QtCore.pyqtSlot()
    def start(self):
        ...
        # self.worker_thread = self.Worker()
        # self.worker_thread.run(self)

    @QtCore.pyqtSlot()
    def _on_kline_event_appeared(self, candle: BitmexExchangeHandler.KlineCallback):
        candle_dict = {
            "Open": candle.open,
            "High": candle.high,
            "Low": candle.low,
            "Close": candle.close,
            "Volume": candle.volume,
        }
        self.chart.add_candle(candle_dict)
