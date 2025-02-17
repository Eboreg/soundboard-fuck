import curses
import curses.panel
import logging
from abc import ABC, abstractmethod
from functools import total_ordering
from typing import TYPE_CHECKING, Self

from soundboard_fuck.ui.base.panel_placement import PanelPlacement
from soundboard_fuck.ui.base.size import Size
from soundboard_fuck.utils import coerce_at_least, split_to_rows


if TYPE_CHECKING:
    from soundboard_fuck.keypress import KeyPress
    from soundboard_fuck.ui.base.screen import Screen


@total_ordering
class BasePanel(ABC):  # pylint: disable=too-many-public-methods
    screen: "Screen"
    z_index: int = 0
    border: bool = False
    create_hidden: bool = False
    panel: "curses.panel._Curses_Panel"  # pylint: disable=no-member
    window: curses.window
    title: str | None = None
    is_popup: bool = False

    def __init__(
        self,
        border: bool | None = None,
        z_index: int | None = None,
        create_hidden: bool | None = None,
        is_popup: bool | None = None,
    ):
        if z_index is not None:
            self.z_index = z_index
        if border is not None:
            self.border = border
        if create_hidden is not None:
            self.create_hidden = create_hidden
        if is_popup is not None:
            self.is_popup = is_popup

    @property
    def height(self) -> int:
        return self.window.getmaxyx()[0]

    @property
    def is_visible(self) -> bool:
        return not self.panel.hidden()

    @property
    def width(self) -> int:
        width = self.window.getmaxyx()[1]
        if self.border:
            return width - 3
        return width - 1

    def __eq__(self, other):
        return other is self

    def __lt__(self, other: Self):
        return self.z_index < other.z_index

    def attach(self, screen: "Screen", window: curses.window):
        self.screen = screen
        self.window = window
        window.erase()
        if self.border:
            window.box()
        self.panel = curses.panel.new_panel(window)
        if self.create_hidden:
            self.hide(refresh=False)
        self.setup()

    def cleanup(self):
        ...

    def clear_line(self, x: int, y: int, width: int | None = None):
        self.set_line(x, y, "", width=width)

    def contents(self):
        if self.border:
            self.window.box()
            self.show_title()

    @abstractmethod
    def get_placement(self, parent: Size) -> PanelPlacement:
        ...

    def hide(self, refresh: bool = True):
        self.screen.hide_panel(self, refresh)

    def move(self, x: int, y: int):
        try:
            self.panel.move(y, x)
        except Exception as e:
            logging.error("%s.move: %s", self.__class__.__name__, str(e))

    def move_to_bottom(self, refresh: bool = True):
        self.screen.move_panel_to_bottom(self, refresh)

    def move_to_top(self, refresh: bool = True):
        self.screen.move_panel_to_top(self, refresh)

    def redraw(self, force: bool = False):
        self.screen.redraw_panel(self, force)

    def resize(self, parent: Size):
        placement = self.get_placement(parent)
        self.window.resize(placement.height, placement.width)
        self.move(placement.x, placement.y)

    def set_line(
        self,
        x: int,
        y: int,
        text: str,
        width: int | None = None,
        attr: int | None = None,
    ):
        if width is None:
            final_width = self.width - x
            # if y >= (self.height - 1):
            #     final_width -= 1
            if self.border:
                final_width -= 2
        else:
            final_width = width
        text = f"{text:{final_width}.{final_width}s}"
        self.window.addstr(y, x, text)
        if attr is not None:
            if width is not None:
                self.window.chgat(y, x, width, attr)
            else:
                self.window.chgat(y, x, -1, attr)

    def set_multiline(
        self,
        x: int,
        y: int,
        text: str,
        width: int | None = None,
        attr: int | None = None,
    ):
        if width is None:
            width = self.width - x - 1
            if self.border:
                width -= 2
        rows = split_to_rows(text, width)
        for idx, row in enumerate(rows):
            if attr is not None:
                self.window.addstr(y + idx, x, row, attr)
            else:
                self.window.addstr(y + idx, x, row)
        return len(rows)

    def set_zindex(self, value: int, refresh: bool = True):
        if value != self.z_index:
            self.z_index = value
            self.screen.reorder_panels(refresh)

    def set_zindex_delta(self, delta: int, refresh: bool = True):
        if delta != 0:
            self.z_index += delta
            self.screen.reorder_panels(refresh)

    def setup(self):
        ...

    def show(self):
        self.screen.show_panel(self)

    def show_title(self):
        if self.title and self.border:
            text = f"[ {self.title} ]"
            x = coerce_at_least(int((self.width - len(text)) / 2), 0)
            self.window.addstr(0, x, text)

    def take(self, key: "KeyPress") -> bool:
        return False
