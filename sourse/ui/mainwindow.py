from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sourse.ui.modules as UiModules
import asyncio
import pandas as pd
import threading
from sourse.marketmaker import MarketMaker
from sourse.exchange_handlers import BitmexExchangeHandler
import typing


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, asyncio_event_loop: asyncio.AbstractEventLoop):
        self.asyncio_event_loop: asyncio.AbstractEventLoop = asyncio_event_loop

        super().__init__()
        uic.loadUi("sourse/ui/mainwindow.ui", self)  # Load the .ui file
        # # self.setWindowIcon(QtGui.QIcon("assets/icon_1.png"))

        self.top_left_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget"
        )
        self.bottom_left_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget_2"
        )
        self.right_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget_3"
        )
        self.bottom_dockwidget: QtWidgets.QDockWidget = self.findChild(
            QtWidgets.QDockWidget, "dockWidget_5"
        )

        self.current_settings = UiModules.CurrentSettingsModule(self.right_dockwidget)

        self.setting_templates = UiModules.SettingTemplatesModule(
            self.bottom_left_dockwidget
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

        self.handle = BitmexExchangeHandler(*self.current_settings.get_current_keys())
        self.chart = UiModules.Chart(self)

        data_loading = asyncio.run_coroutine_threadsafe(
            self.handle.load_historical_data("XBTUSD", "1m", 2000),
            self.asyncio_event_loop,
        )

        self.handle.start_kline_socket_threaded(
            self._on_kline_event_appeared, "1m", "XBTUSD"
        )

        self.chart.draw_historical_data(data_loading.result())

        # data_loading.add_done_callback(
        #     lambda x: self.chart.draw_historical_data(x.result())
        # )

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

            mainwindow.marketmaker.grid_updates.connect(
                lambda x: mainwindow._on_grid_updates(x)
            )
            mainwindow.marketmaker.order_updated.connect(
                lambda x: mainwindow._on_order_updated(x)
            )

            asyncio.run_coroutine_threadsafe(
                mainwindow.marketmaker.start(), mainwindow.asyncio_event_loop
            )

    @QtCore.pyqtSlot()
    def start(self):
        self.worker_thread = self.Worker()
        self.worker_thread.run(self)

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

    @QtCore.pyqtSlot()
    def _on_grid_updates(
        self, orders: typing.List[typing.Tuple[str, float, float, str]]
    ):
        self.current_orders.remove_all_orders()
        self.chart.add_grid(
            [p for d, p, _, _ in orders if d == "Buy"],
            [p for d, p, _, _ in orders if d == "Sell"],
        )

    @QtCore.pyqtSlot()
    def _on_order_updated(self, data: BitmexExchangeHandler.OrderUpdate):
        self.current_orders.add_order(data)
