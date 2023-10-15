import ctypes

from sdl2 import *
from sdl2.sdlttf import *


class Text:
    def __init__(
        self,
        renderer: SDL_Renderer,
        font: TTF_Font,
        text: str,
        color: SDL_Color,
        x: int = 0,
        y: int = 0,
    ):
        surface = TTF_RenderText_Blended(font, text.encode(), color)
        self.texture = SDL_CreateTextureFromSurface(renderer, surface)
        width = ctypes.c_int(0)
        height = ctypes.c_int(0)
        TTF_SizeText(font, text.encode(), ctypes.pointer(width), ctypes.pointer(height))
        self.rect = SDL_Rect(x=x, y=y, w=width, h=height)

    def draw(self, renderer: SDL_Renderer) -> None:
        SDL_RenderCopy(renderer, self.texture, None, self.rect)

    def set_position(self, x: int, y: int) -> None:
        self.rect.x = x
        self.rect.y = y

