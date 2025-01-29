import curses
import curses.panel
from typing import TypeVar

from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.panel import Panel
from soundboard_fuck.ui.base.size import Size


_PanelT = TypeVar("_PanelT", bound=Panel)


class Screen:
    panels: list[_PanelT]
    window: curses.window
    border: bool
    quit: bool = False

    @property
    def window_size(self) -> Size:
        return Size.from_curses(self.window.getmaxyx())

    def __init__(self, border: bool = False):
        self.border = border
        self.panels = []

    def attach_panel(self, panel: _PanelT):
        placement = panel.get_placement(self.window_size)
        window = curses.newwin(placement.height, placement.width, placement.y, placement.x)
        panel.attach(screen=self, window=window)
        self.panels.append(panel)

    def attach_window(self, window: curses.window):
        curses.use_default_colors()
        self.window = window
        if self.border:
            window.box()
        window.clear()
        self.setup()
        for panel in self.create_panels():
            self.attach_panel(panel)
        self.draw()
        self.loop()

    def cleanup(self):
        ...

    def create_panels(self) -> list[_PanelT]:
        return []

    def draw(self):
        self.window.clear()
        curses.panel.update_panels()

        for panel in sorted(self.panels):
            if panel.is_visible:
                panel.contents()
                panel.window.touchwin()
                panel.window.noutrefresh()

        curses.doupdate()

    def handle_keypress(self, key: KeyPress) -> bool:
        return False

    def hide_panel(self, panel: _PanelT, refresh: bool = True):
        panel.panel.hide()
        curses.panel.update_panels()
        if refresh:
            curses.doupdate()

    def loop(self):
        while not self.quit:
            key = KeyPress.get(self.window)

            if key.c == curses.KEY_RESIZE:
                self.on_resize()

            if self.handle_keypress(key):
                continue

            for panel in self.panels:
                if panel.take(key):
                    break

        self.cleanup()

    def move_panel_to_bottom(self, panel: _PanelT, refresh: bool = True):
        z_min = min((p.z_index for p in self.panels if p != panel), default=1)
        panel.set_zindex(z_min - 1, refresh)

    def move_panel_to_top(self, panel: _PanelT, refresh: bool = True):
        z_max = max((p.z_index for p in self.panels if p != panel), default=-1)
        panel.set_zindex(z_max + 1, refresh)

    def on_resize(self):
        self.reattach_panels()
        self.draw()

    def reattach_panels(self):
        for panel in self.panels:
            panel.resize(self.window_size)

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
        curses.curs_set(0)
        curses.set_escdelay(10)
        self.window.keypad(True)

    def show_panel(self, panel: _PanelT, refresh: bool = True):
        panel.panel.show()
        if refresh:
            self.redraw_panel(panel, True)
