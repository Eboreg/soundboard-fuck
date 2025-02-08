import curses
import curses.ascii
from curses.textpad import Textbox, rectangle

from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.elements.form_element import FormElement
from soundboard_fuck.ui.colors import ColorPair


class Input(FormElement[str]):
    window: curses.window
    box: Textbox
    last_key: KeyPress | None = None
    error: str | None = None

    def __init__(
        self,
        parent,
        x=None,
        y=None,
        value=None,
        validator=None,
        on_change = None,
        width: int | None = None,
        inactive_color: ColorPair | None = None,
        active_color: ColorPair | None = None,
        error_color: ColorPair | None = None,
        label: str = "",
    ):
        super().__init__(parent, x, y, value, validator, on_change)
        self.width = width
        self.inactive_color = inactive_color.color_pair() if inactive_color else curses.color_pair(0)
        self.active_color = active_color.color_pair() if active_color else curses.color_pair(0)
        self.error_color = error_color.color_pair() if error_color else curses.color_pair(0)
        self.label = label

    def get_keypress(self) -> KeyPress:
        self.window.move(0, len(self.get_value()) + 1)
        previous_cursor = curses.curs_set(1)
        self.box = Textbox(self.window)
        self.box.edit(self.validate_box)
        self.set_value(self.box.gather().strip())
        curses.curs_set(previous_cursor)

        assert self.last_key is not None
        return self.last_key

    def draw(self):
        width = self.get_width()
        self.window = self.parent.derwin(1, width - 2, self.y + 1, self.x + 1)
        error: str | None = None
        if self.error:
            color = self.error_color
            error = f" {self.error:.{width - 4}s} "
        elif self.is_active:
            color = self.active_color
        else:
            color = self.inactive_color

        self.parent.attron(color)
        rectangle(self.parent, self.y, self.x, self.y + 2, self.x + width)
        if self.label:
            self.parent.addstr(self.y, self.x + 1, f" {self.label} ")
        if error:
            self.parent.addstr(self.y + 2, self.x + 1, error)
        self.window.addstr(0, 1, f"{self.get_value():{width - 4}s}")
        self.parent.attroff(color)
        self.parent.refresh()

    def get_width(self):
        if self.width is not None:
            return self.width
        return self.parent.getmaxyx()[1] - self.x - 3

    def validate_box(self, ch: int) -> int:
        self.last_key = KeyPress(ch)
        if ch in (
            curses.KEY_UP,
            curses.KEY_DOWN,
            curses.KEY_BTAB,  # shift-tab
            curses.KEY_RESIZE,
            curses.ascii.NL,
            curses.ascii.HT,
            curses.ascii.ESC,
            curses.ascii.TAB,
        ):
            return curses.ascii.BEL
        return ch
