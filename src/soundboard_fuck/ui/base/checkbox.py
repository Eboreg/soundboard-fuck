import curses
import curses.ascii

from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.form_element import FormElement


class Checkbox(FormElement[bool]):
    box: curses.window

    def __init__(
        self,
        parent: curses.window,
        x: int,
        y: int,
        value: bool,
        label: str,
        active_color: int = 0,
    ):
        self.parent = parent
        self.value = value
        self.x = x
        self.y = y
        self.label = label
        self.active_color = curses.color_pair(active_color or 0)
        self.box = self.parent.derwin(1, 4, self.y, self.x)

    def activate(self) -> KeyPress:
        self.draw(True)
        while True:
            key = KeyPress.get(self.box)
            if key.c in (curses.ascii.SP, curses.ascii.NL):
                self.value = not self.value
                self.draw(True)
            elif key.c in (
                curses.KEY_UP,
                curses.KEY_DOWN,
                curses.KEY_BTAB,  # shift-tab
                curses.ascii.HT,
                curses.ascii.ESC,
                curses.ascii.TAB,
            ):
                self.draw()
                return key

    def draw(self, active: bool = False):
        if active:
            self.box.attron(self.active_color)
        self.box.addstr(0, 0, "[X]" if self.value else "[ ]")
        self.parent.addstr(self.y, self.x + 4, self.label)
        if active:
            self.box.attroff(self.active_color)
        self.box.refresh()
