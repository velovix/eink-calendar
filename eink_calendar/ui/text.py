from PIL import ImageDraw, ImageFont


class Text:
    def __init__(
        self,
        *,
        draw: ImageDraw.ImageDraw,
        font: ImageFont.FreeTypeFont,
        text: str,
        color: tuple[int, int, int],
        x: int = 0,
        y: int = 0,
        max_chars: int = 0,
    ):
        if max_chars > 0 and len(text) > max_chars:
            text = text[: max_chars - 3] + "..."

        self._draw = draw
        self._font = font
        self._text = text
        self._color = color
        self._x = x
        self._y = y

        self.width = draw.textlength(text, font=font)

    def draw(self) -> None:
        self._draw.text(
            (self._x, self._y), self._text, fill=self._color, font=self._font,
        )

    def set_position(self, x: int, y: int) -> None:
        self._x = x
        self._y = y
