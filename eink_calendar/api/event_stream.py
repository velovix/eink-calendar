from threading import Thread
from queue import Queue, Empty
from time import time, sleep
from typing import Optional

from .client import Client
from .event import Event


class EventStream:
    def __init__(self, client: Client, poll_delay: float = 60):
        self._client = client
        self._poll_delay = poll_delay
        self._output = Queue()
        self._running = True
        self._thread = Thread(target=self._run)
        self._thread.start()

    def get(self) -> Optional[list[Event]]:
        try:
            return self._output.get_nowait()
        except Empty:
            return None

    def close(self) -> None:
        self._running = False
        self._thread.join()

    def _run(self):
        last_poll = 0
        last_api_events = None

        while self._running:
            if time() - last_poll > self._poll_delay:
                print("Polling for events")
                api_events = self._client.get_events()
                if api_events != last_api_events:
                    print("Event changes detected")
                    last_api_events = api_events
                    self._output.put(api_events)

                last_poll = time()

            sleep(0.01)
