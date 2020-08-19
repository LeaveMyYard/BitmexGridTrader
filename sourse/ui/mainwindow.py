from __future__ import annotations

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sourse.ui.modules as UiModules
import asyncio
import traceback
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

        self.current_settings = UiModules.CurrentSettingsModule(
            self.right_dockwidget, self.is_marketmaker_finished
        )

        self.setting_templates = UiModules.SettingTemplatesModule(
            self.bottom_left_dockwidget
        )

        self.setting_templates.template_selected.connect(
            lambda name, settings: self.current_settings.on_template_loaded(
                name, settings
            )
        )

        # current_settings signals
        self.current_settings.templates_updated.connect(
            self.setting_templates.refresh_templates
        )
        self.current_settings.settings_changed.connect(
            self.setting_templates.reset_load_buttons
        )
        self.current_settings.start_button_pressed.connect(self.start)
        self.current_settings.cancel_all_orders.connect(
            self._on_client_cancels_all_orders
        )
        self.current_settings.fill_position.connect(self._on_client_fills_position)

        # current_orders signals
        self.current_orders = UiModules.CurrentOrdersModule(self.bottom_dockwidget)
        self.current_orders.order_canceled.connect(self._on_client_cancels_order)
        self.current_orders.all_orders_canceled.connect(
            self._on_client_cancels_all_orders
        )
        self.current_orders.rebuild_grid.connect(self._on_client_rebuilds_grid)

        self.data_module = UiModules.DataModule(self.top_left_dockwidget)

        self.handle = BitmexExchangeHandler(*self.current_settings.get_current_keys())
        self.chart = UiModules.Chart(self)

        data_loading = asyncio.run_coroutine_threadsafe(
            self.handle.load_historical_data("XBTUSD", "1m", 1000),
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
        def run(self, mainwindow: MainWindow):
            handler = BitmexExchangeHandler(
                *mainwindow.current_settings.get_current_keys()
            )
            mainwindow.marketmaker = MarketMaker(
                "XBTUSD", handler, mainwindow.current_settings.get_current_settings()
            )

            mainwindow.marketmaker.candle_appeared.connect(
                lambda x: mainwindow._on_kline_event_appeared(x)
            )
            mainwindow.marketmaker.period_updated.connect(
                lambda x: mainwindow._on_period_updates(x)
            )
            mainwindow.marketmaker.grid_updates.connect(
                lambda x: mainwindow._on_grid_updates(x)
            )
            mainwindow.marketmaker.order_updated.connect(
                lambda x: mainwindow._on_order_updated(x)
            )
            mainwindow.marketmaker.error_occured.connect(
                lambda x: mainwindow._on_error_occured(x)
            )

            mainwindow.current_settings.settings_changed.connect(
                lambda: mainwindow.marketmaker.update_settings(
                    mainwindow.current_settings.get_current_settings()
                )
            )

            mainwindow.marketmaker.position_updated.connect(
                lambda x: mainwindow.data_module.update_position(x)
            )
            mainwindow.marketmaker.server_position_updated.connect(
                lambda x: mainwindow.data_module.update_position_server(x)
            )
            mainwindow.marketmaker.price_updated.connect(
                lambda x: mainwindow.data_module.update_price(x)
            )
            mainwindow.marketmaker.balance_updated.connect(
                lambda x: mainwindow.data_module.update_balance(x)
            )

            asyncio.run_coroutine_threadsafe(
                mainwindow.marketmaker.start(), mainwindow.asyncio_event_loop
            )

    def is_marketmaker_finished(self) -> typing.Tuple[bool, bool]:
        """is_marketmaker_finished [summary]

        Returns:
            typing.Tuple[bool, bool]: is_position_filled, are_orders_canceled
        """

        if self.marketmaker is None:
            return True, True

        position_filled = self.marketmaker.get_current_position_data().volume == 0
        orders_canceled = self.marketmaker.get_current_orders_count() == 0

        return position_filled, orders_canceled

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
    def _on_period_updates(
        self, current_orders: typing.List[typing.Tuple[str, float, float, str]]
    ):
        self.chart.add_grid(
            [p for d, p, _, _ in current_orders if d == "Buy"],
            [p for d, p, _, _ in current_orders if d == "Sell"],
        )

    @QtCore.pyqtSlot(object)
    def _on_grid_updates(
        self, orders: typing.List[typing.Tuple[str, float, float, str]]
    ):
        self.current_orders.remove_all_orders()

    @QtCore.pyqtSlot(object)
    def _on_order_updated(self, data: BitmexExchangeHandler.OrderUpdate):
        self.current_orders.add_order(data)

    @QtCore.pyqtSlot(str)
    def _on_client_cancels_order(self, client_orderID: str):
        if self.marketmaker is not None:
            asyncio.run_coroutine_threadsafe(
                self.marketmaker.cancel_order(client_orderID), self.asyncio_event_loop
            )

    @QtCore.pyqtSlot()
    def _on_client_cancels_all_orders(self):
        if self.marketmaker is not None:
            asyncio.run_coroutine_threadsafe(
                self.marketmaker.cancel_orders(), self.asyncio_event_loop
            )

    @QtCore.pyqtSlot()
    def _on_client_fills_position(self):
        if self.marketmaker is not None:
            position = self.marketmaker.get_current_position_data()
            try:
                asyncio.run_coroutine_threadsafe(
                    self.handle.create_market_order(
                        "XBTUSD",
                        "Sell" if position.volume > 0 else "Buy",
                        abs(position.volume),
                    ),
                    self.asyncio_event_loop,
                ).result()
            except Exception as error:
                messagebox = QtWidgets.QMessageBox()
                messagebox.setText(
                    f"An error occured while trying to close the position."
                )
                messagebox.setInformativeText(f"[{error.__class__.__name__}] {error}")
                messagebox.setDetailedText(
                    "\n".join(traceback.format_tb(error.__traceback__))
                )
                messagebox.setIcon(QtWidgets.QMessageBox.Critical)
                messagebox.exec()

    @QtCore.pyqtSlot()
    def _on_client_rebuilds_grid(self):
        if self.marketmaker is not None:
            asyncio.run_coroutine_threadsafe(
                self.marketmaker.update_grid(), self.asyncio_event_loop
            )

    @QtCore.pyqtSlot(object)
    def _on_error_occured(self, error: Exception):
        messagebox = QtWidgets.QMessageBox()
        messagebox.setText(f"An error occured in a marketmaker worker.")
        messagebox.setInformativeText(f"[{error.__class__.__name__}] {error}")
        messagebox.setDetailedText("\n".join(traceback.format_tb(error.__traceback__)))
        messagebox.setIcon(QtWidgets.QMessageBox.Warning)
        messagebox.exec()

    def closeEvent(self, event):
        self.current_settings.check_bot_finish_actions()
        return super().closeEvent(event)

