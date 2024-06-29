import datetime
import faulthandler
import logging
import signal
from argparse import ArgumentParser
from pathlib import Path
from types import FrameType

from PIL import Image, ImageDraw, ImageFont

from . import api, ui
from .display import EInkDisplay, MockDisplay

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 448


def main() -> int:
    faulthandler.enable()

    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser(
        description="Displays calendar events on an Inky 7-color display",
    )

    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Do not communicate with an eInk display",
    )

    args = parser.parse_args()

    api_client = api.Client()

    font_file = Path(__file__).parent / "lora.ttf"
    day_font = ImageFont.truetype(str(font_file), 36)
    times_font = ImageFont.truetype(str(font_file), 16)

    stop = False

    def on_sigint(_sig: int, _frame: FrameType | None) -> None:
        nonlocal stop
        stop = True
    signal.signal(signal.SIGINT, on_sigint)

    event_stream = api.EventStream(api_client)

    ui_events: list[ui.Event] = []

    display = MockDisplay() if args.no_display else EInkDisplay()

    while not stop:
        event_stream.check_health()
        display.check_health()

        image = Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        today = datetime.date.today()
        day_text = ui.Text(
            draw=draw,
            font=day_font,
            text=today.strftime("%A, %B %d"),
            color=(0, 0, 0),
        )
        day_text.set_position(int(SCREEN_WIDTH / 2 - day_text.width / 2), 1)
        day_text.draw()

        for ui_event in ui_events:
            ui_event.draw()

        api_events = event_stream.get()
        if api_events is not None:
            ui_events = []

            for api_event in api_events:
                ui_event = ui.Event(
                    draw,
                    times_font,
                    api_event,
                    (ui.Event.HEIGHT + ui.Event.PADDING_BOTTOM) * len(ui_events)
                    + ui.Event.START_Y,
                )
                ui_event.draw()
                ui_events.append(ui_event)

            display.set_image(image)

    logging.info("Waiting for event stream to stop...")
    event_stream.close()
    logging.info("Waiting for display to finish up...")
    display.close()

    return 0
