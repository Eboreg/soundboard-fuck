import curses
import curses.ascii
from curses.textpad import rectangle

from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.form_element import FormElement


class Button(FormElement):
    window: curses.window

    def __init__(
        self,
        parent: curses.window,
        x: int,
        y: int,
        label: str,
        active_color: int = 0,
    ):
        self.parent = parent
        self.x = x
        self.y = y
        self.label = label
        self.active_color = curses.color_pair(active_color or 0)
        self.window = self.parent.derwin(3, self.width + 1, self.y, self.x)

    @property
    def width(self):
        return len(self.label) + 4

    def activate(self):
        self.draw(True)
        while True:
            key = KeyPress.get(self.window)

            if key.c in (
                curses.KEY_UP,
                curses.KEY_DOWN,
                curses.KEY_BTAB,  # shift-tab
                curses.ascii.HT,
                curses.ascii.ESC,
                curses.ascii.TAB,
                curses.ascii.SP,
                curses.ascii.NL,
            ):
                self.draw()
                return key

    def draw(self, active: bool = False):
        if active:
            self.window.attron(self.active_color)
        rectangle(self.window, 0, 0, 2, self.width - 1)
        self.window.addstr(1, 1, f" {self.label} ")
        if active:
            self.window.attroff(self.active_color)
        self.window.refresh()
