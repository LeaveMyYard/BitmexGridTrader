from __future__ import annotations

import asyncio
import time
import json
import traceback
import typing
from datetime import datetime
from dataclasses import dataclass

from sourse.exchange_handlers import AbstractExchangeHandler, BitmexExchangeHandler
from sourse.logger import init_logger
from PyQt5 import QtCore


class MarketMaker(QtCore.QObject):
    """This class encapsulates a handler and starts a marketmaking bot."""

    period_updated = QtCore.pyqtSignal()
    candle_appeared = QtCore.pyqtSignal(object)
    grid_updates = QtCore.pyqtSignal(object)
    order_updated = QtCore.pyqtSignal(object)
    position_updated = QtCore.pyqtSignal(object)
    price_updated = QtCore.pyqtSignal(float)
    balance_updated = QtCore.pyqtSignal(float)
    error_occured = QtCore.pyqtSignal(object)

    @dataclass
    class Settings:
        """The settings object for the marketmaker bot."""

        orders_pairs: int
        orders_start_size: int
        order_step_size: int
        interval: float
        min_spread: float
        stop_loss_fund: float
        rebuild_after_change: float
        adjust_grid_by_position: bool
        min_position: int
        max_position: int

    @dataclass
    class Position:
        volume: int = 0
        price: float = 0

    @staticmethod
    async def minute_start():  # TODO as period_start()
        """minute_start will be working until a new minute starts."""
        duration = 60
        await asyncio.sleep(duration - (time.time() % duration))

    def __init__(
        self,
        pair_name: str,
        handler: AbstractExchangeHandler,
        settings: MarketMaker.Settings,
    ):
        """__init__ Create a new MarketMaker bot.

        Args:
            pair_name (str): [description]
            handler (AbstractExchangeHandler): [description]
            settings (MarketMaker.Settings): [description]
        """
        super().__init__(None)

        self.pair_name = pair_name
        self.handler = handler
        self.update_settings(settings)
        self.position = MarketMaker.Position()
        self.balance = 0.01

        self.logger = init_logger(self.__class__.__name__)

        self._current_orders: typing.Dict[str, str] = {}
        self._current_price: typing.Optional[float] = None
        self._grid_price: typing.Optional[float] = None
        self.__current_grid_orders: typing.List[
            typing.Tuple[str, float, float, str]
        ] = []

    def update_settings(self, settings: MarketMaker.Settings):
        self.settings = settings

    def _on_order_filled(self, order: AbstractExchangeHandler.OrderUpdate):
        if self.position.volume == 0:
            self.position.volume = order.volume
            self.position.price = order.average_price
        elif (
            self.position.volume < 0
            and order.volume < 0
            or self.position.volume > 0
            and order.volume > 0
        ):
            self.position.price = (self.position.volume + order.volume) / (
                order.average_price / order.volume
                + self.position.price / self.position.volume
            )
            self.position.volume += order.volume
        elif abs(self.position.volume) >= abs(order.volume):
            self.position.volume += order.volume
            self.balance += order.volume * (
                -1 / self.position.price + 1 / order.average_price
            )
        else:
            self.balance += self.position.volume * (
                1 / self.position.price - 1 / order.average_price
            )
            self.position.volume += order.volume
            self.position.price = order.average_price

        self.balance -= order.fee

        self.position_updated.emit(self.position)
        self.balance_updated.emit(self.balance)

    def _on_user_update(self, data: AbstractExchangeHandler.UserUpdate):
        if isinstance(data, AbstractExchangeHandler.OrderUpdate):
            self._current_orders[data.orderID] = data.status
            self.logger.debug(
                "Order %s (%s;%s): %s",
                data.orderID,
                data.price,
                data.volume,
                data.status,
            )

            self.order_updated.emit(data)

            if data.status == "CANCELED" or data.status == "FILLED":
                del self._current_orders[data.orderID]
                if data.status == "FILLED":
                    self._on_order_filled(data)

                self.logger.info(
                    "Balance: %s, Position: %s, %s",
                    self.balance,
                    self.position.price,
                    self.position.volume,
                )

        elif isinstance(data, AbstractExchangeHandler.PositionUpdate):
            if data.size != self.position.volume:
                self.logger.warning(
                    "Position, got from server differes with the calculated one: (%s; %s) vs (%s; %s)",
                    data.entry_price,
                    data.size,
                    self.position.price,
                    self.position.volume,
                )

        elif isinstance(data, AbstractExchangeHandler.BalanceUpdate):
            self.balance = data.balance
            self.balance_updated.emit(self.balance)
            self.logger.debug("Updated balance from server: %s", self.balance)

    def _on_price_changed(self, data: AbstractExchangeHandler.PriceCallback):
        self._current_price = data.price
        self.price_updated.emit(self._current_price)

    @staticmethod
    def __convert_order_data(
        price: float, volume: float
    ) -> typing.Tuple[str, float, float]:
        return ("Buy" if volume > 0 else "Sell", price, abs(volume))

    def _generate_orders(self) -> typing.List[typing.Tuple[str, float, float, str]]:
        orders = []

        if self._current_price is None:
            raise RuntimeError(
                "Current price is not loaded yet, can not generate orders"
            )

        used_price = self._current_price
        self._grid_price = used_price

        # Creating short orders
        if self.position.volume > self.settings.min_position:
            for i in range(self.settings.orders_pairs):
                start_price = (
                    self.position.price
                    if self.settings.adjust_grid_by_position
                    and self.position.volume > 0
                    and used_price + self.settings.min_spread // 2 < self.position.price
                    else used_price + self.settings.min_spread // 2
                )
                price = used_price + (
                    self.settings.min_spread // 2 + i * self.settings.interval
                )
                price = round(int(price * 2) / 2, 1)
                volume = -(
                    self.settings.orders_start_size + self.settings.order_step_size * i
                )
                orders.append(
                    (
                        *self.__convert_order_data(price, volume),
                        AbstractExchangeHandler.generate_client_order_id(),
                    )
                )

        # Creating long orders
        if self.position.volume < self.settings.max_position:
            for i in range(self.settings.orders_pairs):
                start_price = (
                    self.position.price
                    if self.settings.adjust_grid_by_position
                    and self.position.volume < 0
                    and used_price - self.settings.min_spread // 2 > self.position.price
                    else used_price - self.settings.min_spread // 2
                )
                price = start_price - i * self.settings.interval
                price = round(int(price * 2) / 2, 1)
                volume = (
                    self.settings.orders_start_size + self.settings.order_step_size * i
                )
                orders.append(
                    (
                        *self.__convert_order_data(price, volume),
                        AbstractExchangeHandler.generate_client_order_id(),
                    )
                )

        return orders

    def get_current_position_data(self) -> MarketMaker.Position:
        return self.position

    def get_current_orders_count(self) -> int:
        return len(self._current_orders)

    async def create_orders(
        self, orders: typing.List[typing.Tuple[str, float, float, str]]
    ):
        self.logger.debug("Creating grid from current price (%s)", self._current_price)
        await self.handler.create_orders(self.pair_name, orders)

    async def cancel_orders(self):
        if len(self._current_orders) > 0:
            await self.handler.cancel_orders(list(self._current_orders.keys()))

    async def cancel_order(self, client_orderID: str):
        await self.handler.cancel_order(client_orderID=client_orderID)

    async def update_grid(self):
        await self.cancel_orders()
        orders = self.__current_grid_orders = self._generate_orders()
        self.grid_updates.emit(orders)
        for order in orders:
            order_update = AbstractExchangeHandler.OrderUpdate(
                orderID="",
                client_orderID=order[3],
                status="PENDING",
                price=order[1],
                average_price=-1,
                fee=0,
                fee_asset="XBT",
                volume=order[2] if order[0] == "Buy" else -order[2],
                volume_realized=0,
                time=None,
                message={},
            )

            self.order_updated.emit(order_update)
        await self.create_orders(orders)

    async def start(self):
        """Start the marketmaker bot."""
        self._working = True

        self.handler.start_user_update_socket_threaded(self._on_user_update)
        self.handler.start_price_socket_threaded(self._on_price_changed, self.pair_name)

        await asyncio.sleep(2)

        while self._working:
            try:
                await MarketMaker.minute_start()
                if self._current_price is None:
                    raise RuntimeError(
                        f"The bot has started, but the price is still not loaded"
                    )

                if self._working:
                    self.period_updated.emit()
                    if (
                        self._grid_price is None
                        or 100
                        * abs(self._grid_price - self._current_price)
                        / self._current_price
                        >= self.settings.rebuild_after_change
                    ):
                        await self.update_grid()
                    else:
                        self.grid_updates.emit(self.__current_grid_orders)
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e.__class__.__name__, e, "\n")
                self.error_occured.emit(e)

    def stop(self):
        self._working = False


def main():
    file_settings = json.load(open("settings.json", "r"))
    handler = BitmexExchangeHandler(
        file_settings["bitmex_client"]["public_key"],
        file_settings["bitmex_client"]["private_key"],
    )
    settings = MarketMaker.Settings(**file_settings["marketmaker_settings"])
    market_maker = MarketMaker(
        file_settings["bitmex_client"]["pair"], handler, settings
    )
    asyncio.run(market_maker.start())


if __name__ == "__main__":
    main()
