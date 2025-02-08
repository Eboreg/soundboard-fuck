from abc import ABC, abstractmethod
import curses
from typing import TypeVar

from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.elements.form_element import FormElement
from soundboard_fuck.ui.colors import ColorPair
from soundboard_fuck.utils import coerce_at_least, coerce_at_most, coerce_between, step_list


_T = TypeVar("_T")


class ScrollableSelect(FormElement[_T], ABC):
    options: list[_T]
    window: curses.window
    label: str = ""
    offset: int = 0

    def __init__(
        self,
        parent: curses.window,
        height: int,
        x=None,
        y=None,
        value=None,
        validator=None,
        on_change=None,
        label: str | None = None,
        options: list[_T] | None = None,
        width: int | None = None,
        inactive_color: ColorPair | None = None,
        active_color: ColorPair | None = None,
        selected_color: ColorPair | None = None,
    ):
        super().__init__(parent, x, y, value, validator, on_change)
        max_height = parent.getmaxyx()[0] - (y or 0)
        self.height = min(height, max_height)
        self.inactive_color = inactive_color.color_pair() if inactive_color else curses.color_pair(0)
        self.active_color = active_color.color_pair() if active_color else curses.color_pair(0)
        self.selected_color = selected_color.color_pair() if selected_color else curses.color_pair(0)
        self.options = options or []
        self.width = width
        if label is not None:
            self.label = label

    @property
    def max_y(self):
        return self.height - 2

    @property
    def selected_idx(self):
        return self.options.index(self.get_value())

    @property
    def visible_indices(self):
        return range(self.offset, self.offset + self.max_y)

    @property
    def visible_options(self):
        return self.options[self.offset:self.offset + self.max_y]

    @abstractmethod
    def print_option_label(self, option: _T, window: curses.window, x: int, y: int, width: int):
        ...

    def draw(self):
        width = self.get_width()
        self.window = self.parent.derwin(self.height, width, self.y, self.x)
        color = self.active_color if self.is_active else self.inactive_color
        self.window.attron(color)
        self.window.box()
        if self.label:
            self.window.addstr(0, 1, f" {self.label} ")
        self.window.attroff(color)
        self.draw_options()
        self.draw_scrollbar()
        self.window.refresh()

    def draw_options(self):
        options = self.visible_options
        value = self.get_value()
        for pos, option in enumerate(options):
            if option == value:
                self.window.attron(self.selected_color)
            self.print_option_label(option, self.window, 2, pos + 1, self.get_width() - 4)
            if option == value:
                self.window.attroff(self.selected_color)
        if len(options) < self.max_y - 1:
            for pos in range(len(options), self.max_y):
                self.window.addstr(pos + 1, 2, " " * (self.get_width() - 4))

    def draw_scrollbar(self):
        max_y = self.max_y
        visible_fraction = max_y / len(self.options)
        bar_height = coerce_between(round(max_y * visible_fraction), 1, max_y)
        pre_bar = coerce_at_most(round((self.offset * max_y) / len(self.options)), max_y - bar_height)
        post_bar = max_y - pre_bar - bar_height
        x = self.get_width() - 1

        for y in range(pre_bar):
            self.window.addstr(y + 1, x, "░")
        for y in range(pre_bar, pre_bar + bar_height):
            self.window.addstr(y + 1, x, "█")
        for y in range(pre_bar + bar_height, pre_bar + bar_height + post_bar):
            self.window.addstr(y + 1, x, "░")

    def get_keypress(self) -> KeyPress:
        while True:
            key = KeyPress.get(self.window)

            if key.c == curses.KEY_RESIZE:
                return key
            if key.c in (
                curses.KEY_UP,
                curses.KEY_DOWN,
                curses.KEY_NPAGE,
                curses.KEY_PPAGE,
                curses.KEY_HOME,
                curses.KEY_END,
            ):
                # KEY_SF = shift-down
                # KEY_SR = shift-up
                if key.c == curses.KEY_UP:
                    self.step(-1)
                elif key.c == curses.KEY_DOWN:
                    self.step(1)
                elif key.c == curses.KEY_NPAGE:
                    self.step(self.max_y, False)
                elif key.c == curses.KEY_PPAGE:
                    self.step(-self.max_y, False)
                elif key.c == curses.KEY_HOME:
                    self.step_to(0)
                elif key.c == curses.KEY_END:
                    self.step_to(len(self.options) - 1)
                self.draw()
            else:
                return key

    def get_value(self):
        if not hasattr(self, "_value"):
            return self.options[0]
        return self._value

    def get_width(self):
        if self.width is not None:
            return self.width
        return self.parent.getmaxyx()[1] - self.x - 1

    def step(self, steps: int, wrap: bool = True):
        new_idx = step_list(self.options, self.selected_idx, steps, wrap)
        self.step_to(new_idx)

    def step_to(self, new_idx: int):
        if new_idx < self.visible_indices.start:
            self.offset = new_idx
        elif new_idx >= self.visible_indices.stop:
            self.offset = coerce_at_least(new_idx - self.max_y + 1, 0)
        self.set_value(self.options[new_idx])
