import curses
import curses.ascii
from curses.textpad import rectangle

from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.elements.form_element import FormElement
from soundboard_fuck.ui.colors import ColorPair


class Button(FormElement):
    window: curses.window

    def __init__(
        self,
        parent,
        label: str,
        x=None,
        y=None,
        value=None,
        validator=None,
        on_change=None,
        active_color: ColorPair | None = None,
        disabled_color: ColorPair | None = None,
        height: int = 3,
        is_disabled: bool | None = None,
        is_active: bool | None = None,
    ):
        super().__init__(parent, x, y, value, validator, on_change)
        self.height = height
        self.label = label
        self.active_color = active_color.color_pair() if active_color else curses.color_pair(0)
        self.disabled_color = disabled_color.color_pair() if disabled_color else curses.color_pair(0)
        if is_disabled is not None:
            self.is_disabled = is_disabled
        if is_active is not None:
            self.is_active = is_active

    @property
    def width(self):
        return max(len(s) for s in self.label.split("\n")) + 4

    def get_keypress(self):
        while True:
            key = KeyPress.get(self.window)

            if key.c == curses.KEY_RESIZE:
                return key
            if key.c in (
                curses.KEY_UP,
                curses.KEY_DOWN,
                curses.KEY_BTAB,  # shift-tab
                curses.ascii.HT,
                curses.ascii.ESC,
                curses.ascii.TAB,
            ):
                self.draw()
                return key
            if key.c in (curses.ascii.SP, curses.ascii.NL) and not self.is_disabled:
                self.draw()
                return key

    def draw(self):
        self.window = self.parent.derwin(self.height, self.width + 1, self.y, self.x)
        if self.is_disabled:
            self.window.attron(self.disabled_color)
        elif self.is_active:
            self.window.attron(self.active_color)
        rectangle(self.window, 0, 0, self.height - 1, self.width - 1)
        for idx, label in enumerate(self.label.split("\n")):
            self.window.addstr(idx + 1, 1, f" {label:{self.width - 3}s}")
        if self.is_disabled:
            self.window.attroff(self.disabled_color)
        elif self.is_active:
            self.window.attroff(self.active_color)
        self.window.refresh()
