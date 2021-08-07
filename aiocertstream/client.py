from asyncio import AbstractEventLoop, get_event_loop
from json import loads
from typing import Coroutine

from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType


class Client:
    def __init__(self, loop: AbstractEventLoop = None, url: str = None) -> None:
        """An async client for certstream.

        Args:
            loop (AbstractEventLoop, optional): The asyncio event loop to run on. Defaults to None.
            url (str, optional): The websocket URL to connect to. Defaults to None.
        """
        self._loop = loop or get_event_loop()
        self._url = url or "wss://certstream.calidog.io/"
        self._session = ClientSession(loop=self._loop)

        self._ws: ClientWebSocketResponse = None
        self._listeners: list = []

    def listen(self, coro: Coroutine) -> Coroutine:
        """Add a response handler coroutine."""

        self._listeners.append(coro)

        return coro

    def run(self) -> None:
        """Make a blocking call to run the client."""

        while True:
            self._loop.run_until_complete(self.start())

    async def dispatch(self, data: dict) -> None:
        """Dispatch a message to all listeners."""

        if data.get("message_type") == "heartbeat":
            return  # TODO: Handle heartbeats

        for listener in self._listeners:
            await listener(data)

    async def _start(self) -> None:
        """Intenally start the websocket."""

        self._ws = await self._session.ws_connect(self._url)

        async for message in self._ws:
            if message.type == WSMsgType.TEXT:
                self._loop.create_task(self.dispatch(loads(message.data)))

    async def start(self, *, reconnect: bool = True) -> None:
        """Start the client."""

        while True:
            await self._start()
            if not reconnect:
                break
