import sdl2
from sdl2 import sdlttf

from eink_calendar import api, ui


class Event:
    HEIGHT = 40
    PADDING_BOTTOM = 10
    START_X = 65
    START_Y = 65
    COLOR_SQUARE_SIZE = 15
    TEXT_X_OFFSET = 30
    TIME_Y_OFFSET = 18

    def __init__(
        self,
        renderer: sdl2.SDL_Renderer,
        font: sdlttf.TTF_Font,
        api_event: api.Event,
        y: int,
    ):
        x = self.START_X

        self.color = sdl2.SDL_Color(
            r=api_event.color[0], g=api_event.color[1], b=api_event.color[2], a=255,
        )

        self.color_square = sdl2.SDL_Rect(
            x=x,
            y=int(y + (self.HEIGHT / 2 - self.COLOR_SQUARE_SIZE / 2)),
            w=self.COLOR_SQUARE_SIZE,
            h=self.COLOR_SQUARE_SIZE,
        )

        if api_event.all_day:
            time_str = "All Day"
        else:
            time_str = api_event.start_time.strftime("%I:%M %p")

        self.time_text = ui.Text(
            renderer=renderer,
            font=font,
            text=time_str,
            color=sdl2.SDL_Color(0, 0, 0, 255),
            x=x + self.TEXT_X_OFFSET,
            y=y,
            max_chars=60,
        )
        self.ui_text = ui.Text(
            renderer=renderer,
            font=font,
            text=api_event.summary,
            color=sdl2.SDL_Color(0, 0, 0, 255),
            x=x + self.TEXT_X_OFFSET,
            y=y + self.TIME_Y_OFFSET,
            max_chars=60,
        )

    def draw(self, renderer: sdl2.SDL_Renderer) -> None:
        sdl2.SDL_SetRenderDrawColor(
            renderer, self.color.r, self.color.g, self.color.b, self.color.a,
        )
        sdl2.SDL_RenderFillRect(renderer, self.color_square)

        self.time_text.draw(renderer)
        self.ui_text.draw(renderer)
