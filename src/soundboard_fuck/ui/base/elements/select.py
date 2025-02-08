import curses
import curses.ascii
import curses.panel
from abc import ABC, abstractmethod
from typing import TypeVar

from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.elements.form_element import FormElement
from soundboard_fuck.ui.colors import ColorPair


_T = TypeVar("_T")


class Select(FormElement[_T], ABC):
    is_open: bool = False
    dropdown_window: curses.window | None = None
    dropdown_panel: "curses.panel._Curses_Panel | None" = None  # pylint: disable=no-member
    options: list[_T]
    window: curses.window
    label: str = ""

    def __init__(
        self,
        parent,
        x=None,
        y=None,
        value=None,
        validator=None,
        on_change=None,
        options: list[_T] | None = None,
        width: int | None = None,
        inactive_color: ColorPair | None = None,
        active_color: ColorPair | None = None,
        selected_color: ColorPair | None = None,
        label: str | None = None,
    ):
        super().__init__(parent, x, y, value, validator, on_change)
        self.inactive_color = inactive_color.color_pair() if inactive_color else curses.color_pair(0)
        self.active_color = active_color.color_pair() if active_color else curses.color_pair(0)
        self.selected_color = selected_color.color_pair() if selected_color else curses.color_pair(0)
        self.options = options or []
        self.width = width
        if label is not None:
            self.label = label

    @abstractmethod
    def print_option_label(self, option: _T, window: curses.window, x: int, y: int, width: int):
        ...

    def draw(self):
        width = self.get_width() - 1
        self.window = self.parent.derwin(4, width + 2, self.y, self.x)
        color = self.active_color if self.is_active else self.inactive_color
        self.window.attron(color)
        self.draw_borders()
        self.window.addstr(1, width - 1, "▴" if self.is_open else "▾")
        if self.label:
            self.window.addstr(0, 1, f" {self.label} ")
        self.window.attroff(color)
        self.print_option_label(self.get_value(), self.window, 2, 1, width - 5)
        self.window.refresh()
        if self.is_open:
            dropdown_window = self.init_dropdown()
            self.draw_dropdown(dropdown_window)
            dropdown_window.refresh()
        else:
            if self.dropdown_panel:
                self.dropdown_panel.hide()
                curses.panel.update_panels()
                curses.doupdate()

    def draw_borders(self):
        width = self.get_width()
        self.window.addch(0, 0, curses.ACS_ULCORNER)
        self.window.addch(0, width, curses.ACS_URCORNER)
        self.window.addch(2, 0, curses.ACS_LTEE if self.is_open else curses.ACS_LLCORNER)
        self.window.addch(2, width, curses.ACS_RTEE if self.is_open else curses.ACS_LRCORNER)
        self.window.addch(1, 0, curses.ACS_VLINE)
        self.window.addch(1, width, curses.ACS_VLINE)
        self.window.hline(0, 1, curses.ACS_HLINE, width - 1)
        self.window.hline(2, 1, curses.ACS_HLINE, width - 1)

    def draw_dropdown(self, window: curses.window):
        height = self.get_height()
        self.draw_dropdown_borders(window, height)
        value = self.get_value()
        selected_idx = self.options.index(value)
        start_idx = 0
        if selected_idx >= height - 1:
            start_idx = min(selected_idx, len(self.options) - height + 1)
        for idx, option in enumerate(self.options[start_idx:start_idx + height - 1]):
            if option == value:
                window.attron(self.selected_color)
            self.print_option_label(option, window, 2, idx, self.get_width() - 3)
            if option == value:
                window.attroff(self.selected_color)

    def draw_dropdown_borders(self, window: curses.window, height: int):
        width = self.get_width()
        window.addch(height - 1, 0, curses.ACS_LLCORNER)
        window.addch(height - 1, width, curses.ACS_LRCORNER)
        window.vline(0, 0, curses.ACS_VLINE, height - 1)
        window.vline(0, width, curses.ACS_VLINE, height - 1)
        window.hline(height - 1, 1, curses.ACS_HLINE, width - 1)

    def get_height(self):
        parent_start_y = self.parent.getbegyx()[0]
        start_y = parent_start_y + self.y + 3
        # pylint: disable=no-member
        end_y = min(curses.LINES, start_y + len(self.options) + 1)
        return end_y - start_y

    def get_keypress(self) -> KeyPress:
        while True:
            key = KeyPress.get(self.window)

            if key.c == curses.KEY_RESIZE:
                return key
            if key.c in (curses.ascii.SP, curses.ascii.NL):
                self.is_open = not self.is_open
                self.draw()
            elif self.is_open and key.c == curses.ascii.ESC:
                self.is_open = False
                self.draw()
            elif self.is_open and key.c in (curses.KEY_UP, curses.KEY_DOWN):
                selected_idx = self.options.index(self.get_value())
                if key.c == curses.KEY_UP:
                    new_idx = selected_idx - 1 if selected_idx > 0 else len(self.options) - 1
                else:
                    new_idx = selected_idx + 1 if selected_idx < len(self.options) - 1 else 0
                self.set_value(self.options[new_idx])
                self.draw()
            elif key.c in (
                curses.KEY_BTAB,  # shift-tab
                curses.ascii.HT,
                curses.ascii.ESC,
                curses.ascii.TAB,
                curses.KEY_UP,
                curses.KEY_DOWN,
            ):
                self.is_open = False
                return key

    def get_value(self):
        if not hasattr(self, "_value"):
            return self.options[0]
        return self._value

    def get_width(self):
        if self.width is not None:
            return self.width
        return self.parent.getmaxyx()[1] - self.x - 3

    def init_dropdown(self) -> curses.window:
        width = self.get_width()
        parent_start_y, parent_start_x = self.parent.getbegyx()
        start_x = parent_start_x + self.x
        start_y = parent_start_y + self.y + 3
        height = self.get_height()
        dropdown_window = curses.newwin(height, width + 2, start_y, start_x)
        self.dropdown_panel = curses.panel.new_panel(dropdown_window)
        self.dropdown_window = dropdown_window
        return dropdown_window
