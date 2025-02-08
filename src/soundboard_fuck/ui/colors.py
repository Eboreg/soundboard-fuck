import curses
import enum
from dataclasses import dataclass


@dataclass
class Color:
    r: int
    g: int
    b: int
    color_number: int

    def init(self):
        curses.init_color(self.color_number, self.r, self.g, self.b)


class Colors:
    WHITE = Color(1000, 1000, 1000, 11)
    RED = Color(804, 192, 192, 12)
    GREEN = Color(51, 737, 475, 13)
    BLUE = Color(141, 447, 784, 14)
    CYAN = Color(0, 680, 680, 15)
    MAGENTA = Color(680, 0, 680, 16)
    YELLOW = Color(680, 680, 0, 17)
    PINK = Color(900, 80, 600, 18)
    ORANGE = Color(1000, 500, 0, 19)
    MINT = Color(0, 1000, 700, 20)
    GRAY = Color(600, 600, 600, 21)

    BLACK = Color(0, 0, 0, 31)
    DARK_GRAY = Color(300, 300, 300, 32)
    DARK_RED = Color(200, 0, 0, 33)
    DARK_GREEN = Color(0, 200, 0, 34)
    DARK_BLUE = Color(0, 0, 200, 35)
    DARK_CYAN = Color(0, 200, 200, 36)
    DARK_MAGENTA = Color(200, 0, 200, 37)
    DARK_YELLOW = Color(200, 200, 0, 38)
    DARK_PINK = Color(300, 30, 200, 39)
    DARK_ORANGE = Color(400, 200, 0, 40)
    DARK_MINT = Color(0, 400, 300, 41)

    @classmethod
    def init_all(cls):
        for value in cls.__dict__.values():
            if isinstance(value, Color):
                value.init()


@dataclass
class ColorPair:
    fg: Color | int
    bg: Color | int
    pair_number: int

    @property
    def fg_int(self) -> int:
        if isinstance(self.fg, Color):
            return self.fg.color_number
        return self.fg

    @property
    def bg_int(self) -> int:
        if isinstance(self.bg, Color):
            return self.bg.color_number
        return self.bg

    @property
    def inverse(self):
        return ColorPair(self.bg, self.fg, self.pair_number + 32)

    def init(self):
        inverse = self.inverse
        curses.init_pair(self.pair_number, self.fg_int, self.bg_int)
        curses.init_pair(inverse.pair_number, inverse.fg_int, inverse.bg_int)

    def color_pair(self):
        if curses.has_colors():
            return curses.color_pair(self.pair_number)
        return 0


class ColorPairs:
    WHITE_ON_BLACK = ColorPair(Colors.WHITE, Colors.BLACK, 11)
    WHITE_ON_DARK_BLUE = ColorPair(Colors.WHITE, Colors.DARK_BLUE, 12)
    WHITE_ON_DARK_CYAN = ColorPair(Colors.WHITE, Colors.DARK_CYAN, 13)
    WHITE_ON_DARK_GREEN = ColorPair(Colors.WHITE, Colors.DARK_GREEN, 14)
    WHITE_ON_DARK_MAGENTA = ColorPair(Colors.WHITE, Colors.DARK_MAGENTA, 15)
    WHITE_ON_DARK_MINT = ColorPair(Colors.WHITE, Colors.DARK_MINT, 16)
    WHITE_ON_DARK_ORANGE = ColorPair(Colors.WHITE, Colors.DARK_ORANGE, 17)
    WHITE_ON_DARK_PINK = ColorPair(Colors.WHITE, Colors.DARK_PINK, 18)
    WHITE_ON_DARK_RED = ColorPair(Colors.WHITE, Colors.DARK_RED, 19)
    WHITE_ON_DARK_YELLOW = ColorPair(Colors.WHITE, Colors.DARK_YELLOW, 20)

    BLACK_ON_BLUE = ColorPair(Colors.BLACK, Colors.BLUE, 21)
    BLACK_ON_CYAN = ColorPair(Colors.BLACK, Colors.CYAN, 22)
    BLACK_ON_GREEN = ColorPair(Colors.BLACK, Colors.GREEN, 23)
    BLACK_ON_MAGENTA = ColorPair(Colors.BLACK, Colors.MAGENTA, 24)
    BLACK_ON_MINT = ColorPair(Colors.BLACK, Colors.MINT, 25)
    BLACK_ON_ORANGE = ColorPair(Colors.BLACK, Colors.ORANGE, 26)
    BLACK_ON_PINK = ColorPair(Colors.BLACK, Colors.PINK, 27)
    BLACK_ON_RED = ColorPair(Colors.BLACK, Colors.RED, 28)
    BLACK_ON_WHITE = ColorPair(Colors.BLACK, Colors.WHITE, 29)
    BLACK_ON_YELLOW = ColorPair(Colors.BLACK, Colors.YELLOW, 30)

    DARK_GRAY_ON_DEFAULT = ColorPair(Colors.DARK_GRAY, -1, 31)
    RED_ON_DEFAULT = ColorPair(Colors.RED, -1, 32)
    GRAY_ON_DEFAULT = ColorPair(Colors.GRAY, -1, 33)

    @classmethod
    def init_all(cls):
        for value in cls.__dict__.values():
            if isinstance(value, ColorPair):
                value.init()


@dataclass
class SchemeColors:
    regular: ColorPair
    selected: ColorPair
    label: str


class ColorScheme(enum.Enum):
    RED = SchemeColors(ColorPairs.WHITE_ON_DARK_RED, ColorPairs.BLACK_ON_RED, "Red")
    GREEN = SchemeColors(ColorPairs.WHITE_ON_DARK_GREEN, ColorPairs.BLACK_ON_GREEN, "Green")
    BLUE = SchemeColors(ColorPairs.WHITE_ON_DARK_BLUE, ColorPairs.BLACK_ON_BLUE, "Blue")
    CYAN = SchemeColors(ColorPairs.WHITE_ON_DARK_CYAN, ColorPairs.BLACK_ON_CYAN, "Cyan")
    MAGENTA = SchemeColors(ColorPairs.WHITE_ON_DARK_MAGENTA, ColorPairs.BLACK_ON_MAGENTA, "Magenta")
    YELLOW = SchemeColors(ColorPairs.WHITE_ON_DARK_YELLOW, ColorPairs.BLACK_ON_YELLOW, "Yellow")
    WHITE = SchemeColors(ColorPairs.WHITE_ON_BLACK, ColorPairs.BLACK_ON_WHITE, "White")
    PINK = SchemeColors(ColorPairs.WHITE_ON_DARK_PINK, ColorPairs.BLACK_ON_PINK, "Pink")
    ORANGE = SchemeColors(ColorPairs.WHITE_ON_DARK_ORANGE, ColorPairs.BLACK_ON_ORANGE, "Orange")
    MINT = SchemeColors(ColorPairs.WHITE_ON_DARK_MINT, ColorPairs.BLACK_ON_MINT, "Mint")


def setup():
    if curses.has_colors() and curses.can_change_color():
        Colors.init_all()
        ColorPairs.init_all()
