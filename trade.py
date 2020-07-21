from __future__ import annotations

import asyncio
import time
import typing
from dataclasses import dataclass

from sourse.exchange_handlers import (AbstractExchangeHandler,
                                      BitmexExchangeHandler)
from sourse.logger import init_logger


class MarketMaker:
    @dataclass
    class Settings:
        orders_pairs: int
        orders_start_size: int
        order_step_size: int
        interval: float
        min_spread: float
        min_position: int
        max_position: int

    @dataclass
    class Position:
        volume: int = 0
        price: float = 0

    @staticmethod
    async def minute_start(): # TODO as period_start()
        while round(time.time() % 60, 2) != 0:
            pass

    def __init__(self, pair_name: str, handler: AbstractExchangeHandler, settings: MarketMaker.Settings):
        self.pair_name = pair_name
        self.handler = handler
        self.settings = settings
        self.position = MarketMaker.Position()
        self.balance = 0.0115

        self.logger = init_logger(self.__class__.__name__)

        self._current_orders: typing.Dict[str, str] = {}
        self._current_price: typing.Optional[float] = None

    def on_order_filled(self, order: AbstractExchangeHandler.OrderUpdate):
        if self.position.volume == 0:
            self.position.volume = order.volume
            self.position.price = order.average_price
        elif self.position.volume < 0 and order.volume < 0 or self.position.volume > 0 and order.volume > 0:
            self.position.price = order.average_price * order.volume + self.position.price * self.position.volume
            self.position.volume += order.volume
            self.position.price /= self.position.volume
        elif abs(self.position.volume) >= abs(order.volume):
            self.position.volume += order.volume
            self.balance += order.volume * (-1 / self.position.price + 1 / order.average_price)
        else:
            self.balance += self.position.volume * (1 / self.position.price - 1 / order.average_price)
            self.position.volume += order.volume
            self.position.price = order.average_price

        self.balance -= order.fee

    def on_user_update(self, data: AbstractExchangeHandler.UserUpdate):
        if isinstance(data, AbstractExchangeHandler.OrderUpdate):
            self._current_orders[data.orderID] = data.status
            self.logger.debug("Order %s (%s;%s): %s", data.orderID, data.price, data.volume, data.status)

            if data.status == "CANCELED" or data.status == "FILLED":
                del self._current_orders[data.orderID]
                if data.status == "FILLED":
                    self.on_order_filled(data)

                self.logger.info("Balance: %s, Position: %s, %s", self.balance, self.position.price, self.position.volume)

    def on_price_changed(self, data: AbstractExchangeHandler.PriceCallback):
        self._current_price = data.price

    async def create_order(self, price: float, volume: float):
        order_data: AbstractExchangeHandler.NewOrderData = await self.handler.create_order(self.pair_name, "Buy" if volume > 0 else "Sell", price, abs(volume))
        self._current_orders[order_data.orderID] = "New"

    async def _create_orders(self):
        orders = []
        self.logger.debug("Creating grid from current price (%s)", self._current_price)
        for i in range(self.settings.orders_pairs):
            if self.position.volume < self.settings.max_position:
                price = self._current_price + self.settings.min_spread // 2 + i * self.settings.interval
                price = round(int(price * 2) / 2, 1)
                volume = self.settings.orders_start_size + self.settings.order_step_size * i
                orders.append(self.create_order(price, volume))

            if self.position.volume > self.settings.min_position:
                price = self._current_price - (self.settings.min_spread // 2 + i * self.settings.interval)
                price = round(int(price * 2) / 2, 1)
                volume = -(self.settings.orders_start_size + self.settings.order_step_size * i)
                orders.append(self.create_order(price, volume))

        await asyncio.gather(*orders)

    async def _cancel_orders(self):
        if len(self._current_orders) == 0:
            pass
        await asyncio.gather(*[self.handler.cancel_order(order) for order in self._current_orders])

    async def start(self):
        self.handler.start_user_update_socket_threaded(self.on_user_update)
        self.handler.start_price_socket_threaded(self.on_price_changed, self.pair_name)

        await asyncio.sleep(2)

        while True:
            await MarketMaker.minute_start()
            await self._cancel_orders()
            await self._create_orders()
        


if __name__ == "__main__":
    handler = BitmexExchangeHandler(
        "VMWmsl1N-EZtSB8HjLmgv4GQ", "kJIvv60NCZu-mFWnxsrOeOAGB4VaEphnEZEZKdzISmZkc5wv"
    )
    settings = MarketMaker.Settings(2, 99, 100, 0.5, 1.5, -30, 30)
    market_maker = MarketMaker("XBTUSD", handler, settings)
    asyncio.run(market_maker.start())
