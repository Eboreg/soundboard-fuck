import curses
import curses.ascii
from curses.textpad import Textbox, rectangle
from typing import Callable

from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.form_element import FormElement


class Input(FormElement[str]):
    window: curses.window
    box: Textbox
    last_key: KeyPress | None = None
    error: str | None = None

    def __init__(
        self,
        parent: curses.window,
        x: int,
        y: int,
        width: int | None = None,
        inactive_color: int = 0,
        active_color: int = 0,
        error_color: int = 0,
        value: str = "",
        label: str = "",
        validator: Callable[[str], str | None] | None = None,
    ):
        self.parent = parent
        self.x = x
        self.y = y
        self.width = width
        self.inactive_color = curses.color_pair(inactive_color)
        self.active_color = curses.color_pair(active_color)
        self.error_color = curses.color_pair(error_color)
        self.value = value
        self.label = label
        self.window = self.parent.derwin(1, self.get_width() - 2, self.y + 1, self.x + 1)
        self.box = Textbox(self.window)
        self.validator = validator

    def activate(self) -> KeyPress:
        self.draw(active=True)
        self.window.move(0, len(self.value) + 1)
        previous_cursor = curses.curs_set(1)
        self.box.edit(self.validate_box)
        self.value = self.box.gather().strip()
        curses.curs_set(previous_cursor)
        if self.validator:
            self.error = self.validator(self.value)
        self.draw()

        assert self.last_key is not None
        return self.last_key

    def draw(self, active: bool = False):
        width = self.get_width()
        error: str | None = None
        if self.error:
            color = self.error_color
            error = f" {self.error:.{width - 4}s} "
        elif active:
            color = self.active_color
        else:
            color = self.inactive_color

        self.parent.attron(color)
        rectangle(self.parent, self.y, self.x, self.y + 2, self.x + width)
        if self.label:
            self.parent.addstr(self.y, self.x + 1, f" {self.label} ")
        if error:
            self.parent.addstr(self.y + 2, self.x + 1, error)
        self.window.addstr(0, 1, f"{self.value:{width - 4}s}")
        self.parent.attroff(color)
        self.parent.refresh()

    def get_width(self):
        if self.width is not None:
            return self.width
        return self.parent.getmaxyx()[1] - self.x - 2

    def validate_box(self, ch: int) -> int:
        self.last_key = KeyPress(ch)
        if ch in (
            curses.KEY_UP,
            curses.KEY_DOWN,
            curses.KEY_BTAB,  # shift-tab
            curses.ascii.NL,
            curses.ascii.HT,
            curses.ascii.ESC,
            curses.ascii.TAB,
        ):
            return curses.ascii.BEL
        return ch
