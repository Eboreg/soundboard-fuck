import curses
from typing import Any

from soundboard_fuck.ui.panels.abstract_panel import AbstractPanel
from soundboard_fuck.ui.base.panel_placement import PanelPlacement
from soundboard_fuck.ui.colors import ColorPairs


class BottomPanel(AbstractPanel):
    def contents(self):
        super().contents()
        selected_sound = self.state.selected_sound
        selected_sounds = self.state.selected_sounds
        width = self.width

        self.window.clear()
        self.window.hline(0, 0, curses.ACS_HLINE, width)

        if selected_sounds:
            selected = len(selected_sounds)
            selected_text = "1 selected sound" if selected == 1 else f"{selected} selected sounds"
            text = (
                f"{selected_text} | Enter/Space to toggle select | "
                "Esc to unselect all"
            )
            self.set_line(0, 1, text)
        elif selected_sound:
            text = (
                f"{selected_sound.duration_seconds:.1f}s | "
                f"{selected_sound.play_count} plays"
            )
            self.set_line(0, 1, text)
        else:
            self.clear_line(0, 1)

        self.print_progress()

    def print_progress(self):
        progress = self.state.play_progress
        width = self.width
        bar_width = width - 25
        bar_x = width - bar_width
        attr = ColorPairs.GRAY_ON_DEFAULT.color_pair()

        if progress is not None:
            filled_width = round(progress * bar_width)
            self.window.addstr(1, bar_x, "█" * filled_width, attr)
            if filled_width < bar_width:
                filler = "░" * (bar_width - filled_width)
                self.window.addstr(1, bar_x + filled_width, filler, attr)
        else:
            self.window.addstr(1, bar_x, " " * bar_width, attr)

    def get_placement(self, parent):
        return PanelPlacement(x=0, y=parent.height - 2, width=parent.width + 1, height=2, parent=parent)

    def on_state_change(self, name: str, value: Any):
        if name in ("selected_sound_id", "selected_sounds", "categories_with_sounds"):
            self.contents()
            curses.doupdate()
        if name == "play_progress":
            self.print_progress()
            curses.doupdate()
