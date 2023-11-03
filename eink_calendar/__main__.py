import sys
import ctypes
import faulthandler
from pathlib import Path
import datetime
import json
from time import sleep, time

from PIL import Image
from sdl2 import *
from sdl2.sdlttf import *
from xdg import BaseDirectory

from . import ui, api
from .display import Display


SCREEN_WIDTH = 600
SCREEN_HEIGHT = 448


def screenshot(window, renderer) -> Image:
    src = SDL_GetWindowSurface(window)
    if not src:
        raise RuntimeError("Could not get window surface")

    pixels = (
        ctypes.c_uint8
        * src.contents.w
        * src.contents.h
        * src.contents.format.contents.BytesPerPixel
    )()
    rc = SDL_RenderReadPixels(
        renderer,
        src.contents.clip_rect,
        src.contents.format.contents.format,
        pixels,
        src.contents.w * src.contents.format.contents.BytesPerPixel,
    )
    if rc != 0:
        raise RuntimeError("Could not call RenderReadPixels")

    dest = SDL_CreateRGBSurfaceFrom(
        pixels,
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
    SDL_SaveBMP(dest, str(image_path).encode())
    return Image.open(image_path)


BLACK = SDL_Color(0, 0, 0)
GRAY = SDL_Color(150, 150, 150)


def main() -> int:
    faulthandler.enable()

    api_client = api.Client()

    if SDL_Init(SDL_INIT_EVERYTHING) != 0:
        print("Could not initialize SDL", file=sys.stderr)
        return -1

    if TTF_Init() != 0:
        print("Could not initialize SDL TTF", file=sys.stderr)
        return -1

    window = SDL_CreateWindow(
        b"eInk Calendar",
        SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        SDL_WINDOW_SHOWN,
    )
    if not window:
        print("Could not create window", file=sys.stderr)
        return -1

    renderer = SDL_CreateRenderer(
        window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
    )
    if not renderer:
        print("Could not create renderer", file=sys.stderr)
        return -1

    font_file = Path(__file__).parent / "lora.ttf"
    day_font = TTF_OpenFont(str(font_file).encode(), 36)
    times_font = TTF_OpenFont(str(font_file).encode(), 16)

    today = datetime.date.today()
    day_text = ui.Text(renderer, day_font, today.strftime("%A, %B %d"), BLACK)
    day_text.set_position(int(SCREEN_WIDTH / 2 - day_text.rect.w / 2), 1)

    quit = False

    event_stream = api.EventStream(api_client)

    ui_events = []

    display = Display()

    while not quit:
        input_event = SDL_Event()
        SDL_PollEvent(input_event)
        if input_event.type == SDL_QUIT:
            quit = True

        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)
        SDL_RenderClear(renderer)

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

        SDL_RenderPresent(renderer)

    print("Waiting for event stream to stop...")
    event_stream.close()
    print("Waiting for display to finish up...")
    display.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
