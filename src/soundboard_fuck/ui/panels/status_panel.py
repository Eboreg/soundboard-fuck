import curses
import curses.ascii
from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.elements.button import Button
from soundboard_fuck.ui.base.panel_placement import CenteredPanelPlacement
from soundboard_fuck.ui.colors import ColorPairs
from soundboard_fuck.ui.panels.abstract_panel import AbstractPanel
from soundboard_fuck.utils import split_to_rows


class StatusPanel(AbstractPanel):
    rows: list[str]

    def __init__(self, state, db, text: str, z_index=None, show_cancel_button: bool = False):
        self.rows = split_to_rows(text, 56)
        self.show_cancel_button = show_cancel_button
        super().__init__(state=state, db=db, border=True, z_index=z_index, create_hidden=False, is_popup=True)

    def check_cancellation(self) -> bool:
        if self.show_cancel_button:
            key = KeyPress.get_non_blocking(self.window)
            if key and key.c in (curses.ascii.NL, curses.ascii.SP):
                return True
        return False

    def contents(self):
        super().contents()
        for idx, row in enumerate(self.rows):
            self.set_line(2, 2 + idx, row)
        if self.show_cancel_button:
            button = Button(
                parent=self.window,
                label="Cancel",
                x=2,
                y=self.height - 4,
                active_color=ColorPairs.BLACK_ON_BLUE,
                is_active=True,
            )
            button.draw()

    def get_placement(self, parent):
        return CenteredPanelPlacement(
            parent=parent,
            width=60,
            height=len(self.rows) + 8 if self.show_cancel_button else 4,
        )

    def set_text(self, text: str):
        self.rows = split_to_rows(text, 56)
        if self.is_visible:
            self.resize(self.screen.window_size)
            self.redraw(force=True)
