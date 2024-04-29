import ctypes

import sdl2
from sdl2 import sdlttf


class Text:
    def __init__(
        self,
        *,
        renderer: sdl2.SDL_Renderer,
        font: sdlttf.TTF_Font,
        text: str,
        color: sdl2.SDL_Color,
        x: int = 0,
        y: int = 0,
        max_chars: int = 0,
    ):
        if max_chars > 0 and len(text) > max_chars:
            text = text[: max_chars - 3] + "..."

        surface = sdlttf.TTF_RenderText_Blended(font, text.encode(), color)
        self.texture = sdl2.SDL_CreateTextureFromSurface(renderer, surface)
        width = ctypes.c_int(0)
        height = ctypes.c_int(0)
        sdlttf.TTF_SizeText(
            font, text.encode(), ctypes.pointer(width), ctypes.pointer(height),
        )
        self.rect = sdl2.SDL_Rect(x=x, y=y, w=width, h=height)

    def draw(self, renderer: sdl2.SDL_Renderer) -> None:
        sdl2.SDL_RenderCopy(renderer, self.texture, None, self.rect)

    def set_position(self, x: int, y: int) -> None:
        self.rect.x = x
        self.rect.y = y
