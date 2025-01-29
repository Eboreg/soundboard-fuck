import curses
import enum
from dataclasses import dataclass


BLACK_ON_WHITE = 10
BLACK_ON_RED = 12
BLACK_ON_GREEN = 13
BLACK_ON_BLUE = 14
BLACK_ON_CYAN = 15
BLACK_ON_MAGENTA = 16
BLACK_ON_YELLOW = 17

WHITE_ON_BLACK = 20
WHITE_ON_DARK_RED = 22
WHITE_ON_DARK_GREEN = 23
WHITE_ON_DARK_BLUE = 24
WHITE_ON_DARK_CYAN = 25
WHITE_ON_DARK_MAGENTA = 26
WHITE_ON_DARK_YELLOW = 27

DARK_GRAY_ON_DEFAULT = 30
RED_ON_DEFAULT = 31


@dataclass
class SchemeColors:
    regular: int
    selected: int
    label: str


class ColorScheme(enum.Enum):
    RED = SchemeColors(regular=WHITE_ON_DARK_RED, selected=BLACK_ON_RED, label="Red")
    GREEN = SchemeColors(regular=WHITE_ON_DARK_GREEN, selected=BLACK_ON_GREEN, label="Green")
    BLUE = SchemeColors(regular=WHITE_ON_DARK_BLUE, selected=BLACK_ON_BLUE, label="Blue")
    CYAN = SchemeColors(regular=WHITE_ON_DARK_CYAN, selected=BLACK_ON_CYAN, label="Cyan")
    MAGENTA = SchemeColors(regular=WHITE_ON_DARK_MAGENTA, selected=BLACK_ON_MAGENTA, label="Magenta")
    YELLOW = SchemeColors(regular=WHITE_ON_DARK_YELLOW, selected=BLACK_ON_YELLOW, label="Yellow")
    BLACK = SchemeColors(regular=WHITE_ON_BLACK, selected=BLACK_ON_WHITE, label="Black")


@dataclass
class Color:
    color_number: int
    r: int
    g: int
    b: int


class Colors(enum.Enum):
    WHITE = Color(11, 1000, 1000, 1000)
    RED = Color(12, 804, 192, 192)
    GREEN = Color(13, 51, 737, 475)
    BLUE = Color(14, 141, 447, 784)
    CYAN = Color(15, 0, 680, 680)
    MAGENTA = Color(16, 680, 0, 680)
    YELLOW = Color(17, 680, 680, 0)
    BLACK = Color(21, 0, 0, 0)
    DARK_GRAY = Color(22, 300, 300, 300)
    DARK_RED = Color(23, 200, 0, 0)
    DARK_GREEN = Color(24, 0, 200, 0)
    DARK_BLUE = Color(25, 0, 0, 200)
    DARK_CYAN = Color(26, 0, 200, 200)
    DARK_MAGENTA = Color(27, 200, 0, 200)
    DARK_YELLOW = Color(28, 200, 200, 0)


def init_pair(pair_number: int, fg: Colors | int, bg: Colors | int):
    if isinstance(fg, Colors):
        fg = fg.value.color_number
    if isinstance(bg, Colors):
        bg = bg.value.color_number
    curses.init_pair(pair_number, fg, bg)


def setup():
    if curses.has_colors():
        if curses.can_change_color():
            for v in Colors:
                curses.init_color(v.value.color_number, v.value.r, v.value.g, v.value.b)

            init_pair(WHITE_ON_BLACK, Colors.WHITE, Colors.BLACK)
            init_pair(WHITE_ON_DARK_RED, Colors.WHITE, Colors.DARK_RED)
            init_pair(WHITE_ON_DARK_GREEN, Colors.WHITE, Colors.DARK_GREEN)
            init_pair(WHITE_ON_DARK_BLUE, Colors.WHITE, Colors.DARK_BLUE)
            init_pair(WHITE_ON_DARK_CYAN, Colors.WHITE, Colors.DARK_CYAN)
            init_pair(WHITE_ON_DARK_MAGENTA, Colors.WHITE, Colors.DARK_MAGENTA)
            init_pair(WHITE_ON_DARK_YELLOW, Colors.WHITE, Colors.DARK_YELLOW)

            init_pair(BLACK_ON_WHITE, Colors.BLACK, Colors.WHITE)
            init_pair(BLACK_ON_RED, Colors.BLACK, Colors.RED)
            init_pair(BLACK_ON_GREEN, Colors.BLACK, Colors.GREEN)
            init_pair(BLACK_ON_BLUE, Colors.BLACK, Colors.BLUE)
            init_pair(BLACK_ON_CYAN, Colors.BLACK, Colors.CYAN)
            init_pair(BLACK_ON_MAGENTA, Colors.BLACK, Colors.MAGENTA)
            init_pair(BLACK_ON_YELLOW, Colors.BLACK, Colors.YELLOW)
            init_pair(DARK_GRAY_ON_DEFAULT, Colors.DARK_GRAY, -1)
            init_pair(RED_ON_DEFAULT, Colors.RED, -1)
        else:
            curses.init_pair(WHITE_ON_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(BLACK_ON_RED, curses.COLOR_BLACK, curses.COLOR_RED)
            curses.init_pair(BLACK_ON_GREEN, curses.COLOR_BLACK, curses.COLOR_GREEN)
            curses.init_pair(BLACK_ON_BLUE, curses.COLOR_BLACK, curses.COLOR_BLUE)
            curses.init_pair(BLACK_ON_CYAN, curses.COLOR_BLACK, curses.COLOR_CYAN)
            curses.init_pair(BLACK_ON_MAGENTA, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
            curses.init_pair(BLACK_ON_YELLOW, curses.COLOR_BLACK, curses.COLOR_YELLOW)
