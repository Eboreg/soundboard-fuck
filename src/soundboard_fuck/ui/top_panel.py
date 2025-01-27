import curses
from typing import TYPE_CHECKING, Any

from soundboard_fuck.ui.abstract_panel import AbstractPanel
from soundboard_fuck.ui.base.panel_placement import PanelPlacement


if TYPE_CHECKING:
    from soundboard_fuck.keypress import KeyPress


class TopPanel(AbstractPanel):
    special_keys = [
        curses.KEY_BACKSPACE,
        curses.KEY_DOWN,
        curses.KEY_END,
        curses.KEY_ENTER,
        curses.KEY_HOME,
        curses.KEY_LEFT,
        curses.KEY_UP,
        curses.KEY_RIGHT,
        curses.KEY_IC, # ins
        curses.KEY_DC, # del
        curses.KEY_PPAGE, # pgup
        curses.KEY_NPAGE, # pgdn
        curses.KEY_RESIZE,
        27, # esc
        ord("\t"),
        ord("\n"),
        *range(curses.KEY_F1, curses.KEY_F12),
    ]

    def contents(self):
        self.set_line(0, 0, f"Filter: {self.state.query}", width=self.width - 28)
        self.set_line(self.width - 40, 0, f"Re-press mode: {self.state.repress_mode.value}")
        self.set_line(self.width - 15, 0, "Help: Alt+H")

    def get_placement(self, parent):
        return PanelPlacement(x=0, y=0, width=parent.width, height=2, parent=parent)

    def on_state_change(self, name: str, value: Any):
        if name in ("query", "repress_mode"):
            self.redraw(force=True)

    def setup(self):
        self.window.border(" ", " ", " ", 0, " ", " ", curses.ACS_HLINE, curses.ACS_HLINE)

    def take(self, key: "KeyPress") -> bool:
        if key.c >= 32 and key.c not in self.special_keys and not key.meta and key.s is not None:
            self.state.query += key.s
            return True

        if key.c == curses.KEY_BACKSPACE:
            if self.state.query:
                if key.meta:
                    self.state.query = ""
                else:
                    self.state.query = self.state.query[:-1]
            return True

        return False
