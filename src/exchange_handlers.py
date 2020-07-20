import abc
import typing
import bitmex
import threading
import base64
import hashlib
from datetime import datetime


class AbstractExchangeHandler(metaclass=abc.ABCMeta):
    def __init__(self, public_key: str, private_key: str):
        self._public_key = public_key
        self._private_key = private_key

    @abc.abstractmethod
    def start_kline_socket(
        self, on_update: typing.Callable[[typing.Mapping[str, typing.Any]], None]
    ) -> None:
        ...

    @abc.abstractmethod
    def start_user_update_socket(
        self, on_update: typing.Callable[[typing.Mapping[str, typing.Any]], None]
    ) -> None:
        ...

    def start_kline_socket_threaded(
        self, on_update: typing.Callable[[typing.Mapping[str, typing.Any]], None]
    ) -> threading.Thread:
        thread = threading.Thread(target=self.start_kline_socket, args=[on_update])
        thread.start()
        return thread

    def start_user_update_socket_threaded(
        self, on_update: typing.Callable[[typing.Mapping[str, typing.Any]], None]
    ) -> threading.Thread:
        thread = threading.Thread(
            target=self.start_user_update_socket, args=[on_update]
        )
        thread.start()
        return thread

    @abc.abstractmethod
    async def create_order(
        self, symbol: str, side: str, price: float, volume: float
    ) -> typing.Any:
        ...

    @abc.abstractmethod
    async def cancel_order(self, order_id: int) -> None:
        ...

    @staticmethod
    def generate_order_id() -> str:
        return base64.b32encode(
            hashlib.sha1(bytes(str(datetime.now()), "utf-8")).digest()
        ).decode("ascii")


class BitmexExchangeHandler(AbstractExchangeHandler):
    def __init__(self, public_key, private_key):
        super().__init__(public_key, private_key)
        self._client = bitmex.bitmex(
            test=False, api_key=self._public_key, api_secret=self._private_key
        )

    def start_kline_socket(
        self, on_update: typing.Callable[[typing.Mapping[str, typing.Any]], None]
    ) -> None:
        ...

    def start_user_update_socket(
        self, on_update: typing.Callable[[typing.Mapping[str, typing.Any]], None]
    ) -> None:
        ...

    async def create_order(
        self, symbol: str, side: str, price: float, volume: float
    ) -> typing.Any:
        return self._client.Order.Order_new(
            clOrdID=self.generate_order_id(),
            symbol=symbol,
            side=side,
            orderQty=volume,
            price=price,
            ordType="Limit",
        ).result()

    async def cancel_order(self, order_id: int) -> None:
        ...
