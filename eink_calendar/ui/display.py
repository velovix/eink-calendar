import ctypes
from pathlib import Path

import sdl2
from PIL import Image
from sdl2 import sdlttf
from xdg import BaseDirectory


class SDLError(Exception):
    pass


def init_display(
    screen_width: int, screen_height: int,
) -> tuple[sdl2.SDL_Window, sdl2.SDL_Renderer]:
    """Initializes SDL and creates a window and renderer"""
    if sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) != 0:
        raise SDLError("Could not initialize SDL")

    if sdlttf.TTF_Init() != 0:
        raise SDLError("Could not initialize SDL TTF")

    window = sdl2.SDL_CreateWindow(
        b"eInk Calendar",
        sdl2.SDL_WINDOWPOS_CENTERED,
        sdl2.SDL_WINDOWPOS_CENTERED,
        screen_width,
        screen_height,
        sdl2.SDL_WINDOW_SHOWN,
    )
    if not window:
        raise SDLError("Could not create window")

    renderer = sdl2.SDL_CreateRenderer(
        window, -1, sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC,
    )
    if not renderer:
        raise SDLError("Could not create renderer")

    return window, renderer


def screenshot(window: sdl2.SDL_Window, renderer: sdl2.SDL_Renderer) -> Image.Image:
    """Captures the contents of the window as a PIL image"""
    src = sdl2.SDL_GetWindowSurface(window)
    if not src:
        raise SDLError("Could not get window surface")

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
        raise SDLError("Could not call RenderReadPixels")

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
        raise SDLError("Could not CreateRGBSurfaceFrom")

    cache_path = Path(BaseDirectory.save_cache_path("eink_calendar"))
    image_path = cache_path / "render.bmp"
    sdl2.SDL_SaveBMP(dest, str(image_path).encode())
    return Image.open(image_path)
