from PIL import ImageDraw, ImageFont

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
        draw: ImageDraw.ImageDraw,
        font: ImageFont.FreeTypeFont,
        api_event: api.Event,
        y: int,
    ):
        self._draw = draw
        self.x = self.START_X
        self.y = y
        self.color = api_event.color

        if api_event.all_day:
            time_str = "All Day"
        else:
            time_str = api_event.start_time.strftime("%I:%M %p")

        self.time_text = ui.Text(
            draw=draw,
            font=font,
            text=time_str,
            color=(0, 0, 0),
            x=self.x + self.TEXT_X_OFFSET,
            y=self.y,
            max_chars=60,
        )
        self.ui_text = ui.Text(
            draw=draw,
            font=font,
            text=api_event.summary,
            color=(0, 0, 0),
            x=self.x + self.TEXT_X_OFFSET,
            y=self.y + self.TIME_Y_OFFSET,
            max_chars=60,
        )

    def draw(self) -> None:
        rect_x = self.x
        rect_y = int(self.y + (self.HEIGHT / 2 - self.COLOR_SQUARE_SIZE / 2))
        self._draw.rectangle(
            (
                rect_x,
                rect_y,
                rect_x + self.COLOR_SQUARE_SIZE,
                rect_y + self.COLOR_SQUARE_SIZE,
            ),
            fill=self.color,
        )

        self.time_text.draw()
        self.ui_text.draw()
