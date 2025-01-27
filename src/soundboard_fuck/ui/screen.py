import curses
from typing import TYPE_CHECKING

from soundboard_fuck.db.sqlitedb import SqliteDb
from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.state import State
from soundboard_fuck.ui import colors
from soundboard_fuck.ui.base.screen import Screen, Size
from soundboard_fuck.ui.bottom_panel import BottomPanel
from soundboard_fuck.ui.error_panel import ErrorPanel
from soundboard_fuck.ui.help_panel import HelpPanel
from soundboard_fuck.ui.sound_batch_edit_panel import SoundBatchEditPanel
from soundboard_fuck.ui.sound_panel import SoundPanel
from soundboard_fuck.ui.top_panel import TopPanel


if TYPE_CHECKING:
    from soundboard_fuck.db.abstractdb import AbstractDb


class SoundboardScreen(Screen):
    top_panel: TopPanel
    bottom_panel: BottomPanel
    sound_panel: SoundPanel
    help_panel: HelpPanel
    error_panel: ErrorPanel
    sound_batch_edit_panel: SoundBatchEditPanel
    db: "AbstractDb"
    quit: bool = False
    state: State

    def __init__(self, border = False):
        super().__init__(border)
        self.db = SqliteDb()
        self.state = State(self.db)
        self.keycodes = {v: k for k, v in curses.__dict__.items() if k.startswith("KEY_")}

    @property
    def window_height(self):
        return self.window.getmaxyx()[0]

    @property
    def window_width(self):
        return self.window.getmaxyx()[1]

    def loop(self):
        while not self.quit:
            wch = self.window.get_wch()
            key = KeyPress(wch, meta=False)

            if key.c == 27:
                self.window.nodelay(True)
                c = self.window.getch()
                key = KeyPress(c, meta=True)
                self.window.nodelay(False)

            if key.c == curses.KEY_RESIZE:
                self.on_resize()
            elif key.meta and key.s == "q":
                self.quit = True
            elif key.meta and key.s == "r":
                self.state.cycle_repress_mode()
            elif key.ctrl and key.s == "d":
                self.quit = True

            self.sound_batch_edit_panel.take(key) or \
                self.help_panel.take(key) or \
                self.top_panel.take(key) or \
                self.sound_panel.take(key)

        self.sound_panel.stop_all()

    def on_resize(self):
        self.screen_state.size = Size.from_curses(self.window.getmaxyx())

    def reattach_panels(self):
        self.top_panel.resize(self.window_width, 2)
        self.bottom_panel.resize(self.window_width, 2)
        self.sound_panel.resize(self.window_width, self.window_height - 4)
        help_placement = self.get_centered_panel_placement(80, self.help_panel.height)
        self.help_panel.move(help_placement.x, help_placement.y)
        self.error_panel.resize(self.window_width - 62, self.window_height - 2)
        sound_batch_edit_placement = self.get_centered_panel_placement(80, 10)
        self.sound_batch_edit_panel.move(sound_batch_edit_placement.x, sound_batch_edit_placement.y)

    def setup(self):
        colors.setup()
        curses.curs_set(0)
        curses.set_escdelay(10)
        self.window.keypad(True)

    def setup_panels(self):
        self.top_panel = TopPanel(state=self.state)
        self.attach_panel(self.top_panel, self.window_width, 2)

        self.bottom_panel = BottomPanel(state=self.state)
        self.attach_panel(self.bottom_panel, self.window_width, 2, 0, self.window_height - 2)

        self.sound_panel = SoundPanel(state=self.state, db=self.db)
        self.attach_panel(self.sound_panel, self.window_width, self.window_height - 4, 0, 2)

        self.help_panel = HelpPanel(state=self.state, z_index=2)
        self.attach_centered_panel(self.help_panel, 80, self.help_panel.height, show=False)

        self.error_panel = ErrorPanel(z_index=1)
        self.attach_panel(
            panel=self.error_panel,
            width=self.window_width - 62,
            height=self.window_height - 3,
            x=61,
            y=3,
            show=False,
        )

        self.sound_batch_edit_panel = SoundBatchEditPanel(state=self.state, db=self.db, z_index=2)
        self.attach_centered_panel(self.sound_batch_edit_panel, 80, 10, show=False)
