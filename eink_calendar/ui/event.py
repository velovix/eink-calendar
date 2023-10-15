import ctypes

from sdl2 import *
from sdl2.sdlttf import *

from .. import api, ui


class Event:
    HEIGHT = 40
    PADDING_BOTTOM = 10
    WIDTH = 470
    THICKNESS = 4

    START_X = 65
    START_Y = 65

    def __init__(
        self, renderer: SDL_Renderer, font: TTF_Font, api_event: api.Event, y: int
    ):
        x = self.START_X

        self.color = SDL_Color(
            r=api_event.color[0], g=api_event.color[1], b=api_event.color[2], a=255
        )

        self.rect = SDL_Rect(x=x, y=y, w=self.WIDTH, h=self.HEIGHT)
        self.inner_rect = SDL_Rect(
            x=x + self.THICKNESS,
            y=y + self.THICKNESS,
            w=self.WIDTH - self.THICKNESS * 2,
            h=self.HEIGHT - self.THICKNESS * 2,
        )

        text = ""
        if not api_event.all_day:
            time_str = api_event.start_time.strftime("%I:%M %p")
            text += f"{time_str} - "
        text += f"{api_event.summary}"

        self.ui_text = ui.Text(renderer, font, text, SDL_Color(0, 0, 0, 255), x, y)
        self.ui_text.set_position(x + 10, int(y + (self.ui_text.rect.h / 2)))

    def draw(self, renderer: SDL_Renderer) -> None:
        SDL_SetRenderDrawColor(
            renderer, self.color.r, self.color.g, self.color.b, self.color.a
        )
        SDL_RenderFillRect(renderer, self.rect)

        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)
        SDL_RenderFillRect(renderer, self.inner_rect)

        self.ui_text.draw(renderer)
