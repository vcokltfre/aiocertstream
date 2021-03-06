from asyncio import AbstractEventLoop, get_event_loop, sleep
from json import loads
from traceback import print_exc
from typing import Coroutine

from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType, ServerDisconnectedError


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

    def run(self, reconnect: bool = True) -> None:
        """Make a blocking call to run the client."""

        self._loop.run_until_complete(self.start(reconnect=reconnect))

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

        backoff = 0.5

        while True:
            try:
                await sleep(backoff)
                await self._start()
                backoff = 0.5
            except Exception:
                print_exc()
                if backoff < 5:
                    backoff *= 2
            if not reconnect:
                break
