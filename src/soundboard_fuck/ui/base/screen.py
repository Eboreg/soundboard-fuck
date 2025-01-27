import curses
import curses.panel
import logging
from dataclasses import dataclass
from typing import Any, TypeVar

from soundboard_fuck.state import AbstractState
from soundboard_fuck.ui.base.panel import Panel


_PanelT = TypeVar("_PanelT", bound=Panel)


@dataclass
class Size:
    width: int
    height: int

    @classmethod
    def from_curses(cls, yx: tuple[int, int]):
        return cls(width=yx[1], height=yx[0])


@dataclass
class PanelPlacement:
    x: int
    y: int
    width: int
    height: int


class ScreenState(AbstractState):
    size: Size

    def __init__(self, width: int = 0, height: int = 0):
        super().__init__()
        self.size = Size(width, height)


class Screen:
    panels: list[_PanelT]
    screen_state: ScreenState
    window: curses.window
    border: bool

    def __init__(self, border: bool = False):
        self.border = border
        self.panels = []
        self.screen_state = ScreenState()

    def attach_centered_panel(self, panel: _PanelT, width: int, height: int, show: bool = True):
        placement = self.get_centered_panel_placement(width, height)
        self.attach_panel(
            panel=panel,
            width=placement.width,
            height=placement.height,
            x=placement.x,
            y=placement.y,
            show=show,
        )

    def attach_panel(self, panel: _PanelT, width: int, height: int, x: int = 0, y: int = 0, show: bool = True):
        height = min(height, self.screen_state.size.height - y)
        width = min(width, self.screen_state.size.width - x)
        window = curses.newwin(height, width, y, x)
        panel.attach(screen=self, window=window, show=show)
        self.panels.append(panel)

    def attach_window(self, window: curses.window):
        self.window = window
        self.screen_state.size = Size.from_curses(window.getmaxyx())
        if self.border:
            window.box()
        window.clear()
        self.screen_state.on_change(self.on_screen_state_change)
        self.setup()
        self.setup_panels()
        self.draw()
        self.loop()

    def draw(self):
        self.window.clear()
        curses.panel.update_panels()
        for panel in sorted(self.panels):
            if panel.is_visible:
                panel.contents()
                panel.window.touchwin()
                panel.window.noutrefresh()
        curses.doupdate()

    def get_centered_panel_placement(self, width: int, height: int) -> PanelPlacement:
        width = min(width, self.screen_state.size.width)
        height = min(height, self.screen_state.size.height)
        x = int((self.screen_state.size.width - width) / 2)
        y = int((self.screen_state.size.height - height) / 2)
        return PanelPlacement(x=x, y=y, width=width, height=height)

    def hide_panel(self, panel: _PanelT, refresh: bool = True):
        panel.panel.hide()
        curses.panel.update_panels()
        if refresh:
            curses.doupdate()

    def loop(self):
        ...

    def move_panel_to_bottom(self, panel: _PanelT, refresh: bool = True):
        z_min = min((p.z_index for p in self.panels if p != panel), default=1)
        panel.set_zindex(z_min - 1, refresh)

    def move_panel_to_top(self, panel: _PanelT, refresh: bool = True):
        z_max = max((p.z_index for p in self.panels if p != panel), default=-1)
        panel.set_zindex(z_max + 1, refresh)

    def on_screen_state_change(self, name: str, value: Any):
        if name == "size":
            logging.info("size=%s; start", value)
            self.reattach_panels()
            self.draw()

    def reattach_panels(self):
        ...

    def redraw_panel(self, panel: _PanelT, force: bool = False):
        if panel.is_visible:
            if panel.window.is_wintouched() or force:
                curses.panel.update_panels()
                if force:
                    panel.contents()
                panel.window.noutrefresh()
                for p in sorted(p for p in self.panels if p.z_index > panel.z_index and p.is_visible):
                    p.contents()
                    p.window.touchwin()
                    p.window.noutrefresh()
                self.window.noutrefresh()
                curses.doupdate()

    def reorder_panels(self, refresh: bool = True):
        for p in sorted(self.panels):
            p.panel.top()
        curses.panel.update_panels()
        if refresh:
            curses.doupdate()

    def setup(self):
        ...

    def setup_panels(self):
        ...

    def show_panel(self, panel: _PanelT, refresh: bool = True):
        panel.panel.show()
        if refresh:
            self.redraw_panel(panel, True)
