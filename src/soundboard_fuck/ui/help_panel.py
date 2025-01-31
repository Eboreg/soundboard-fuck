import curses
import curses.ascii
from typing import TYPE_CHECKING, Any

from soundboard_fuck.ui.abstract_panel import AbstractPanel
from soundboard_fuck.ui.base.panel_placement import CenteredPanelPlacement


if TYPE_CHECKING:
    from soundboard_fuck.keypress import KeyPress
    from soundboard_fuck.state import State


class HelpPanel(AbstractPanel):
    create_hidden = True
    border = True
    title = "Help"

    def __init__(self, state: "State", z_index = 0):
        super().__init__(state=state, z_index=z_index)

    def contents(self):
        super().contents()
        for idx, row in enumerate(self.get_rows()):
            self.set_line(2, 1 + idx, row)

    def get_placement(self, parent):
        return CenteredPanelPlacement(parent=parent, width=80, height=len(self.get_rows()) + 2)

    def get_rows(self) -> list[str]:
        return [
            "Enter: Play/stop/restart sound (depending on re-press mode)",
            "Ctrl+Space: Enter/exit sound selection mode",
            "Ctrl+D/Alt+Q: Quit",
            "Alt+Backspace: Clear filter",
            f"Alt+R: Switch re-press mode (currently: {self.state.meta.repress_mode.value})",
            "Esc: Close open popup",
            "Alt+E: Edit selected sound/category",
            "Alt+N: Add new category",
        ]

    def on_state_change(self, name: str, value: Any):
        if name == "meta" and self.state.show_help:
            self.redraw(force=True)
        if name == "show_help":
            if value is True:
                self.show()
            else:
                self.hide()

    def take(self, key: "KeyPress") -> bool:
        if key.meta and key.s == "h" and not self.state.show_help:
            self.state.show_help = True
            return True
        if key.c == curses.ascii.ESC and self.state.show_help:
            self.state.show_help = False
            return True
        return self.state.show_help
