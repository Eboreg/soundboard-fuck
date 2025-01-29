import curses
from typing import Any

from soundboard_fuck.ui.abstract_panel import AbstractPanel
from soundboard_fuck.ui.base.panel_placement import PanelPlacement


class BottomPanel(AbstractPanel):
    def contents(self):
        selected_sound = self.state.selected_sound
        selected_sounds = self.state.selected_sounds

        if selected_sounds:
            selected = len(selected_sounds)
            selected_text = "1 selected sound" if selected == 1 else f"{selected} selected sounds"
            text = (
                f"{selected_text} | Enter/Space to toggle select | "
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
        elif self.state.selected_category_id:
            self.set_line(0, 1, "Enter: Collapse/expand sounds | Alt+E: Edit category")
        else:
            self.clear_line(0, 1)

    def get_placement(self, parent):
        return PanelPlacement(x=0, y=parent.height - 2, width=parent.width, height=2, parent=parent)

    def on_state_change(self, name: str, value: Any):
        if name in ("selected_sound_id", "selected_sounds", "categories_with_sounds"):
            self.redraw(force=True)

    def setup(self):
        self.window.border(" ", " ", curses.ACS_HLINE, " ", curses.ACS_HLINE, curses.ACS_HLINE, " ", " ")
