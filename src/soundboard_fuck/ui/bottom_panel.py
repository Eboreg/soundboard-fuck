import curses
from typing import Any

from soundboard_fuck.ui.abstract_panel import AbstractPanel


class BottomPanel(AbstractPanel):
    def contents(self):
        selected_sound = self.state.selected_sound
        selected_sounds = self.state.selected_sounds

        if selected_sounds:
            selected = len(selected_sounds)
            selected_text = "1 selected sound" if selected == 1 else f"{selected} selected sounds"
            text = (
                f"{selected_text} | Enter to select/unselect | "
                "Ctrl+Space to unselect all"
            )
            self.set_line(0, 1, text)
        elif selected_sound:
            text = (
                f"{selected_sound.duration_seconds:.1f}s | "
                f"{selected_sound.play_count} plays | "
                f"{selected_sound.path}"
            )
            self.set_line(0, 1, text)
        else:
            self.clear_line(0, 1)

    def on_state_change(self, name: str, value: Any):
        if name in ("selected_sound_id", "selected_sounds", "categories_with_sounds"):
            self.redraw(force=True)

    def setup(self):
        self.window.border(" ", " ", curses.ACS_HLINE, " ", curses.ACS_HLINE, curses.ACS_HLINE, " ", " ")
