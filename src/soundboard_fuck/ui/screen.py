import curses
from typing import TYPE_CHECKING

from soundboard_fuck.db.sqlitedb import SqliteDb
from soundboard_fuck.state import State
from soundboard_fuck.ui import colors
from soundboard_fuck.ui.base.screen import Screen
from soundboard_fuck.ui.bottom_panel import BottomPanel
from soundboard_fuck.ui.error_panel import ErrorPanel
from soundboard_fuck.ui.help_panel import HelpPanel
from soundboard_fuck.ui.sound_batch_edit_panel import SoundBatchEditPanel
from soundboard_fuck.ui.sound_panel import SoundPanel
from soundboard_fuck.ui.top_panel import TopPanel


if TYPE_CHECKING:
    from soundboard_fuck.db.abstractdb import AbstractDb


class SoundboardScreen(Screen):
    sound_panel: SoundPanel
    db: "AbstractDb"
    quit: bool = False
    state: State

    def __init__(self, border = False):
        super().__init__(border)
        self.db = SqliteDb()
        self.state = State(self.db)

    def cleanup(self):
        self.sound_panel.stop_all()

    def handle_keypress(self, key):
        if key.meta and key.s == "q":
            self.quit = True
            return True
        if key.meta and key.s == "r":
            self.state.cycle_repress_mode()
            return True
        if key.ctrl and key.s == "d":
            self.quit = True
            return True

        return False

    def setup(self):
        colors.setup()
        curses.curs_set(0)
        curses.set_escdelay(10)
        self.window.keypad(True)

    def create_panels(self):
        self.sound_panel = SoundPanel(state=self.state, db=self.db)

        return [
            SoundBatchEditPanel(state=self.state, db=self.db, z_index=2),
            HelpPanel(state=self.state, z_index=2),
            TopPanel(state=self.state),
            self.sound_panel,
            BottomPanel(state=self.state),
            ErrorPanel(state=self.state, z_index=1),
        ]
