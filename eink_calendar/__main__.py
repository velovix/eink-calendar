import ctypes
import faulthandler
from pathlib import Path
import datetime
from argparse import ArgumentParser
import logging

from PIL import Image
import sdl2
from sdl2 import sdlttf
from xdg import BaseDirectory

from . import ui, api
from .display import MockDisplay, EInkDisplay


SCREEN_WIDTH = 600
SCREEN_HEIGHT = 448


def screenshot(window: sdl2.SDL_Window, renderer: sdl2.SDL_Renderer) -> Image:
    src = sdl2.SDL_GetWindowSurface(window)
    if not src:
        raise RuntimeError("Could not get window surface")

    pixel_data = (
        ctypes.c_uint8
        * src.contents.w
        * src.contents.h
        * src.contents.format.contents.BytesPerPixel
    )()
    rc = sdl2.SDL_RenderReadPixels(
        renderer,
        src.contents.clip_rect,
        src.contents.format.contents.format,
        pixel_data,
        src.contents.w * src.contents.format.contents.BytesPerPixel,
    )
    if rc != 0:
        raise RuntimeError("Could not call RenderReadPixels")

    dest = sdl2.SDL_CreateRGBSurfaceFrom(
        pixel_data,
        src.contents.w,
        src.contents.h,
        src.contents.format.contents.BitsPerPixel,
        src.contents.w * src.contents.format.contents.BytesPerPixel,
        src.contents.format.contents.Rmask,
        src.contents.format.contents.Gmask,
        src.contents.format.contents.Bmask,
        src.contents.format.contents.Amask,
    )
    if not dest:
        raise RuntimeError("Could not CreateRGBSurfaceFrom")

    cache_path = Path(BaseDirectory.save_cache_path("eink_calendar"))
    image_path = cache_path / "render.bmp"
    sdl2.SDL_SaveBMP(dest, str(image_path).encode())
    return Image.open(image_path)


BLACK = sdl2.SDL_Color(0, 0, 0)
GRAY = sdl2.SDL_Color(150, 150, 150)


def main() -> int:
    faulthandler.enable()

    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser(
        description="Displays calendar events on an Inky 7-color display"
    )

    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Do not communicate with an eInk display",
    )

    args = parser.parse_args()

    api_client = api.Client()

    if sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) != 0:
        logging.error("Could not initialize SDL")
        return -1

    if sdlttf.TTF_Init() != 0:
        logging.error("Could not initialize SDL TTF")
        return -1

    window = sdl2.SDL_CreateWindow(
        b"eInk Calendar",
        sdl2.SDL_WINDOWPOS_CENTERED,
        sdl2.SDL_WINDOWPOS_CENTERED,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        sdl2.SDL_WINDOW_SHOWN,
    )
    if not window:
        logging.error("Could not create window")
        return -1

    renderer = sdl2.SDL_CreateRenderer(
        window, -1, sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
    )
    if not renderer:
        logging.error("Could not create renderer")
        return -1

    font_file = Path(__file__).parent / "lora.ttf"
    day_font = sdlttf.TTF_OpenFont(str(font_file).encode(), 36)
    times_font = sdlttf.TTF_OpenFont(str(font_file).encode(), 16)

    today = datetime.date.today()
    day_text = ui.Text(renderer, day_font, today.strftime("%A, %B %d"), BLACK)
    day_text.set_position(int(SCREEN_WIDTH / 2 - day_text.rect.w / 2), 1)

    stop = False

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

            image = screenshot(window, renderer)
            display.set_image(image)

        sdl2.SDL_RenderPresent(renderer)

    logging.info("Waiting for event stream to stop...")
    event_stream.close()
    logging.info("Waiting for display to finish up...")
    display.close()

    return 0
