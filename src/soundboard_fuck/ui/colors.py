import curses
import enum
from dataclasses import dataclass


BLACK = 10
WHITE = 11
RED = 12
GREEN = 13
BLUE = 14
CYAN = 15
MAGENTA = 16
YELLOW = 17

DARK_GRAY = 21
DARK_RED = 22
DARK_GREEN = 23
DARK_BLUE = 24
DARK_CYAN = 25
DARK_MAGENTA = 26
DARK_YELLOW = 27

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


@dataclass
class SchemeColors:
    regular: int
    selected: int


class ColorScheme(enum.Enum):
    RED = SchemeColors(regular=WHITE_ON_DARK_RED, selected=BLACK_ON_RED)
    GREEN = SchemeColors(regular=WHITE_ON_DARK_GREEN, selected=BLACK_ON_GREEN)
    BLUE = SchemeColors(regular=WHITE_ON_DARK_BLUE, selected=BLACK_ON_BLUE)
    CYAN = SchemeColors(regular=WHITE_ON_DARK_CYAN, selected=BLACK_ON_CYAN)
    MAGENTA = SchemeColors(regular=WHITE_ON_DARK_MAGENTA, selected=BLACK_ON_MAGENTA)
    YELLOW = SchemeColors(regular=WHITE_ON_DARK_YELLOW, selected=BLACK_ON_YELLOW)
    BLACK = SchemeColors(regular=WHITE_ON_BLACK, selected=BLACK_ON_WHITE)


def setup():
    if curses.has_colors():
        if curses.can_change_color() and curses.COLORS >= 24:
            curses.init_color(BLACK, 0, 0, 0)
            curses.init_color(WHITE, 1000, 1000, 1000)
            curses.init_color(RED, 804, 192, 192)
            curses.init_color(GREEN, 51, 737, 475)
            curses.init_color(BLUE, 141, 447, 784)
            curses.init_color(CYAN, 0, 680, 680)
            curses.init_color(MAGENTA, 680, 0, 680)
            curses.init_color(YELLOW, 680, 680, 0)

            curses.init_color(DARK_GRAY, 300, 300, 300)
            curses.init_color(DARK_RED, 200, 0, 0)
            curses.init_color(DARK_GREEN, 0, 200, 0)
            curses.init_color(DARK_BLUE, 0, 0, 200)
            curses.init_color(DARK_CYAN, 0, 200, 200)
            curses.init_color(DARK_MAGENTA, 200, 0, 200)
            curses.init_color(DARK_YELLOW, 200, 200, 0)

            curses.init_pair(WHITE_ON_BLACK, WHITE, BLACK)
            curses.init_pair(WHITE_ON_DARK_RED, WHITE, DARK_RED)
            curses.init_pair(WHITE_ON_DARK_GREEN, WHITE, DARK_GREEN)
            curses.init_pair(WHITE_ON_DARK_BLUE, WHITE, DARK_BLUE)
            curses.init_pair(WHITE_ON_DARK_CYAN, WHITE, DARK_CYAN)
            curses.init_pair(WHITE_ON_DARK_MAGENTA, WHITE, DARK_MAGENTA)
            curses.init_pair(WHITE_ON_DARK_YELLOW, WHITE, DARK_YELLOW)

            curses.init_pair(BLACK_ON_WHITE, BLACK, WHITE)
            curses.init_pair(BLACK_ON_RED, BLACK, RED)
            curses.init_pair(BLACK_ON_GREEN, BLACK, GREEN)
            curses.init_pair(BLACK_ON_BLUE, BLACK, BLUE)
            curses.init_pair(BLACK_ON_CYAN, BLACK, CYAN)
            curses.init_pair(BLACK_ON_MAGENTA, BLACK, MAGENTA)
            curses.init_pair(BLACK_ON_YELLOW, BLACK, YELLOW)
        else:
            curses.init_pair(WHITE_ON_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(BLACK_ON_RED, curses.COLOR_BLACK, curses.COLOR_RED)
            curses.init_pair(BLACK_ON_GREEN, curses.COLOR_BLACK, curses.COLOR_GREEN)
            curses.init_pair(BLACK_ON_BLUE, curses.COLOR_BLACK, curses.COLOR_BLUE)
            curses.init_pair(BLACK_ON_CYAN, curses.COLOR_BLACK, curses.COLOR_CYAN)
            curses.init_pair(BLACK_ON_MAGENTA, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
            curses.init_pair(BLACK_ON_YELLOW, curses.COLOR_BLACK, curses.COLOR_YELLOW)
