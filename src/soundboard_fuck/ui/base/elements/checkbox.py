import curses
import curses.ascii

from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.elements.form_element import FormElement
from soundboard_fuck.ui.colors import ColorPair


class Checkbox(FormElement[bool]):
    box: curses.window

    def __init__(
        self,
        parent,
        label: str,
        value: bool,
        x=None,
        y=None,
        validator=None,
        on_change=None,
        active_color: ColorPair | None = None,
    ):
        super().__init__(parent, x, y, value, validator, on_change)
        self.label = label
        self.active_color = active_color.color_pair() if active_color else curses.color_pair(0)

    def get_keypress(self) -> KeyPress:
        while True:
            key = KeyPress.get(self.box)
            if key.c == curses.KEY_RESIZE:
                return key
            if key.c in (curses.ascii.SP, curses.ascii.NL):
                self.set_value(not self.get_value())
                self.draw()
            elif key.c in (
                curses.KEY_UP,
                curses.KEY_DOWN,
                curses.KEY_BTAB,  # shift-tab
                curses.ascii.HT,
                curses.ascii.ESC,
                curses.ascii.TAB,
            ):
                return key

    def draw(self):
        self.box = self.parent.derwin(1, 4, self.y, self.x)
        if self.is_active:
            self.box.attron(self.active_color)
        self.box.addstr(0, 0, "[X]" if self.get_value() else "[ ]")
        self.parent.addstr(self.y, self.x + 4, self.label)
        if self.is_active:
            self.box.attroff(self.active_color)
        self.box.refresh()
