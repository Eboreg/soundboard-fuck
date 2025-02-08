import curses
import curses.ascii
from typing import TYPE_CHECKING, Any

from soundboard_fuck.ui.panels.abstract_panel import AbstractPanel
from soundboard_fuck.ui.base.panel_placement import CenteredPanelPlacement


if TYPE_CHECKING:
    from soundboard_fuck.keypress import KeyPress


class HelpPanel(AbstractPanel):
    create_hidden = True
    border = True
    title = "Help"
    is_popup = True

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
            "Alt+S: Settings",
            "Alt+A: Add sounds",
        ]

    def on_state_change(self, name: str, value: Any):
        if name == "meta" and self.is_visible:
            self.redraw(force=True)

    def take(self, key: "KeyPress") -> bool:
        if not self.state.is_popup_open:
            if key.meta and key.s == "h":
                self.show()
                return True
        if key.c == curses.ascii.ESC and self.is_visible:
            self.hide()
            return True
        return self.is_visible
