from typing import TYPE_CHECKING, Any

from soundboard_fuck.ui.abstract_panel import AbstractPanel


if TYPE_CHECKING:
    from soundboard_fuck.keypress import KeyPress
    from soundboard_fuck.state import State


class HelpPanel(AbstractPanel):
    def __init__(self, state: "State", z_index = 0):
        super().__init__(state=state, border=True, z_index=z_index)

    @property
    def height(self):
        return len(self.get_rows()) + 2

    def contents(self):
        self.set_title("Help")
        for idx, row in enumerate(self.get_rows()):
            self.set_line(0, idx, row)

    def get_rows(self) -> list[str]:
        return [
            "Enter: Play/stop/restart sound (depending on re-press mode)",
            "Up/Down/PgUp/PgDn/Home/End: Navigate sounds",
            "Ctrl+Space: Enter/exit sound selection mode",
            "Ctrl+D/Alt+Q: Quit",
            "Alt+Backspace: Clear filter",
            f"Alt+R: Switch re-press mode (currently: {self.state.repress_mode.value})",
        ]

    def on_state_change(self, name: str, value: Any):
        if name == "repress_mode" and self.state.show_help:
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
        if key.escape and self.state.show_help:
            self.state.show_help = False
            return True
        return self.state.show_help
