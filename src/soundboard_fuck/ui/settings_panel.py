import curses.ascii
import time
from soundboard_fuck.db.abstractdb import AbstractDb
from soundboard_fuck.ui import colors
from soundboard_fuck.ui.abstract_panel import AbstractPanel
from soundboard_fuck.ui.base.button import Button
from soundboard_fuck.ui.base.checkbox import Checkbox
from soundboard_fuck.ui.base.form_panel import FormPanel
from soundboard_fuck.ui.base.panel_placement import CenteredPanelPlacement
from soundboard_fuck.utils import get_local_sounds_dir


class SettingsPanel(FormPanel, AbstractPanel):
    create_hidden = True
    border = True
    title = "Settings"

    def __init__(self, state, db: AbstractDb, border=None, z_index=None):
        self.db = db
        super().__init__(state, border, z_index)

    def contents(self):
        super().contents()
        height = self.set_multiline(
            x=3,
            y=4,
            text="Will convert all present and future non-WAV sounds to WAV files for low latency."
        )
        self.set_line(3, 5 + height, "Location of converted WAV files:")
        self.set_multiline(3, 6 + height, str(get_local_sounds_dir()))

    def create_elements(self):
        return {
            "convert_to_wav": Checkbox(
                parent=self.window,
                x=3,
                y=2,
                label="Convert all sounds to WAV",
                active_color=colors.BLACK_ON_BLUE,
                value=self.state.meta.convert_to_wav,
            ),
            "save": Button(self.window, 2, 10, label="Save", active_color=colors.BLACK_ON_BLUE),
        }

    def get_placement(self, parent):
        return CenteredPanelPlacement(parent=parent, width=80, height=15)

    def on_element_keypress(self, elem_key, element, key):
        if elem_key == "save" and key.c in (curses.ascii.SP, curses.ascii.NL):
            convert_to_wav = self.get_elements()["convert_to_wav"].value
            self.db.meta_adapter.update(self.state.meta, convert_to_wav=convert_to_wav)
            if convert_to_wav:
                self.window.clear()
                self.window.box()
                self.set_multiline(
                    x=3,
                    y=2,
                    text="Converting existing sounds to WAV, this could take a moment ...",
                )
                self.redraw()
                time.sleep(3)
            return False
        return True

    def take(self, key):
        if key.meta and key.s.lower() == "s":
            self.window.clear()
            self.show()
            return True
        return super().take(key)
