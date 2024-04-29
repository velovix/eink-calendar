from abc import ABC, abstractmethod
from queue import Empty, Queue
from threading import Thread

from inky import Inky7Colour
from PIL import Image


class Display(ABC):
    @abstractmethod
    def set_image(self, image: Image.Image) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


class MockDisplay(Display):
    def set_image(self, image: Image.Image) -> None:
        pass

    def close(self) -> None:
        pass


class EInkDisplay(Display):
    def __init__(self) -> None:
        self._inky = Inky7Colour()
        self._image_queue = Queue[Image.Image]()
        self._running = True
        self._thread = Thread(target=self._run)
        self._thread.start()

    def set_image(self, image: Image.Image) -> None:
        self._image_queue.put(image)

    def close(self) -> None:
        self._running = False
        self._thread.join()

    def _run(self) -> None:
        while self._running:
            try:
                image = self._image_queue.get(timeout=1)
                self._inky.set_image(image)
                self._inky.show()
            except Empty:
                pass
