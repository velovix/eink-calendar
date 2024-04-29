import datetime
import faulthandler
import logging
import signal
from argparse import ArgumentParser
from pathlib import Path
from types import FrameType

import sdl2
from sdl2 import sdlttf

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

    try:
        window, renderer = ui.init_display(SCREEN_WIDTH, SCREEN_HEIGHT)
    except ui.SDLError as ex:
        logging.error(f"{ex}")
        return -1

    font_file = Path(__file__).parent / "lora.ttf"
    day_font = sdlttf.TTF_OpenFont(str(font_file).encode(), 36)
    times_font = sdlttf.TTF_OpenFont(str(font_file).encode(), 16)

    stop = False

    def on_sigint(_sig: int, _frame: FrameType | None) -> None:
        nonlocal stop
        stop = True
    signal.signal(signal.SIGINT, on_sigint)

    event_stream = api.EventStream(api_client)

    ui_events: list[ui.Event] = []

    display = MockDisplay() if args.no_display else EInkDisplay()

    while not stop:
        input_event = sdl2.SDL_Event()
        sdl2.SDL_PollEvent(input_event)
        if input_event.type == sdl2.SDL_QUIT:
            stop = True

        sdl2.SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)
        sdl2.SDL_RenderClear(renderer)

        today = datetime.date.today()
        day_text = ui.Text(
            renderer=renderer,
            font=day_font,
            text=today.strftime("%A, %B %d"),
            color=sdl2.SDL_Color(0, 0, 0),
        )
        day_text.set_position(int(SCREEN_WIDTH / 2 - day_text.rect.w / 2), 1)
        day_text.draw(renderer)

        for ui_event in ui_events:
            ui_event.draw(renderer)

        api_events = event_stream.get()
        if api_events is not None:
            ui_events = []

            for api_event in api_events:
                ui_event = ui.Event(
                    renderer,
                    times_font,
                    api_event,
                    (ui.Event.HEIGHT + ui.Event.PADDING_BOTTOM) * len(ui_events)
                    + ui.Event.START_Y,
                )
                ui_event.draw(renderer)
                ui_events.append(ui_event)

            image = ui.screenshot(window, renderer)
            display.set_image(image)

        sdl2.SDL_RenderPresent(renderer)

    logging.info("Waiting for event stream to stop...")
    event_stream.close()
    logging.info("Waiting for display to finish up...")
    display.close()

    return 0
