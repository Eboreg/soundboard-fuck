import curses
import curses.ascii
import curses.panel
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from soundboard_fuck.keypress import KeyPress


_T = TypeVar("_T")


class Select(ABC, Generic[_T]):
    value: _T
    is_open: bool = False
    dropdown_window: curses.window | None = None
    dropdown_panel: "curses.panel._Curses_Panel | None" = None  # pylint: disable=no-member
    options: list[_T]
    window: curses.window

    def __init__(
        self,
        parent: curses.window,
        x: int,
        y: int,
        options: list[_T] | None = None,
        width: int | None = None,
        inactive_color: int = 0,
        active_color: int = 0,
        selected_color: int = 0,
    ):
        self.inactive_color = curses.color_pair(inactive_color)
        self.active_color = curses.color_pair(active_color)
        self.selected_color = curses.color_pair(selected_color)
        self.parent = parent
        self.options = options or []
        self.width = width
        self.x = x
        self.y = y

    @abstractmethod
    def print_label(self, option: _T, window: curses.window, x: int, y: int, width: int):
        ...

    def activate(self) -> KeyPress:
        self.draw(True)
        while True:
            key = KeyPress.get(self.window)
            if key.c == curses.KEY_RESIZE:
                return key
            if key.c in (curses.ascii.SP, curses.ascii.NL):
                self.is_open = not self.is_open
                self.draw(True)
            elif self.is_open and key.c == curses.ascii.ESC:
                self.is_open = False
                self.draw(True)
            elif self.is_open and key.c in (curses.KEY_UP, curses.KEY_DOWN):
                selected_idx = self.options.index(self.value)
                if key.c == curses.KEY_UP:
                    new_idx = selected_idx - 1 if selected_idx > 0 else len(self.options) - 1
                else:
                    new_idx = selected_idx + 1 if selected_idx < len(self.options) - 1 else 0
                self.value = self.options[new_idx]
                self.draw(True)
            elif key.c in (
                curses.KEY_BTAB,  # shift-tab
                curses.ascii.HT,
                curses.ascii.ESC,
                curses.ascii.TAB,
                curses.KEY_UP,
                curses.KEY_DOWN,
            ):
                self.is_open = False
                self.draw()
                return key

    def draw(self, active: bool = False):
        width = self.get_width()
        self.window = self.parent.derwin(4, width + 1, self.y, self.x)
        color = self.active_color if active else self.inactive_color
        self.window.attron(color)
        self.draw_borders()
        self.window.addstr(1, width - 3, "▴" if self.is_open else "▾")
        self.window.attroff(color)
        self.print_label(self.value, self.window, 2, 1, width - 5)
        self.window.refresh()
        if self.is_open:
            self.init_dropdown()
            self.draw_dropdown()
            if self.dropdown_window:
                self.dropdown_window.refresh()
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

    def draw_dropdown(self):
        height = self.get_height()
        self.draw_dropdown_borders(self.dropdown_window, height)
        selected_idx = self.options.index(self.value)
        start_idx = 0
        if selected_idx >= height - 1:
            start_idx = min(selected_idx, len(self.options) - height + 1)
        for idx, option in enumerate(self.options[start_idx:start_idx + height - 1]):
            if option == self.value:
                self.dropdown_window.attron(self.selected_color)
            self.print_label(option, self.dropdown_window, 2, idx, self.get_width() - 4)
            if option == self.value:
                self.dropdown_window.attroff(self.selected_color)

    def draw_dropdown_borders(self, window: curses.window, height: int):
        width = self.get_width() - 1
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

    def get_width(self):
        if self.width is not None:
            return self.width
        return self.parent.getmaxyx()[1] - self.x - 2

    def init_dropdown(self):
        width = self.get_width()
        parent_start_y, parent_start_x = self.parent.getbegyx()
        start_x = parent_start_x + self.x
        start_y = parent_start_y + self.y + 3
        height = self.get_height()
        self.dropdown_window = curses.newwin(height, width + 1, start_y, start_x)
        self.dropdown_panel = curses.panel.new_panel(self.dropdown_window)
