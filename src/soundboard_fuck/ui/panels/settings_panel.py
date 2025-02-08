import curses.ascii
import enum
from typing import TypedDict

from soundboard_fuck.db.sqlite.comparison import NotLike
from soundboard_fuck.ui.base.elements.button import Button
from soundboard_fuck.ui.base.elements.checkbox import Checkbox
from soundboard_fuck.ui.base.panel_placement import CenteredPanelPlacement
from soundboard_fuck.ui.colors import ColorPairs
from soundboard_fuck.ui.panels.form_panel import FormPanel
from soundboard_fuck.utils import get_local_sounds_dir


class Phase(enum.Enum):
    CHANGE_SETTINGS = enum.auto()
    CONVERT_TO_WAV = enum.auto()


class Elements(TypedDict):
    convert_to_wav: Checkbox
    save: Button


class SettingsPanel(FormPanel):
    create_hidden = True
    border = True
    title = "Settings"
    phase: Phase = Phase.CHANGE_SETTINGS
    is_popup = True
    elements: Elements

    def contents(self):
        if self.phase == Phase.CHANGE_SETTINGS:
            super().contents()
            height = self.set_multiline(
                x=7,
                y=3,
                text="Will convert all present and future non-WAV sounds to WAV files for low latency."
            )
            self.set_line(3, 5 + height, "Location of converted WAV files:")
            self.set_multiline(3, 6 + height, str(get_local_sounds_dir()))
        elif self.phase == Phase.CONVERT_TO_WAV:
            self.set_multiline(x=3, y=2, text="Converting existing sounds to WAV, this could take a moment ...")

    def create_elements(self):
        return {
            "convert_to_wav": Checkbox(
                parent=self.window,
                x=3,
                y=2,
                label="Convert all sounds to WAV",
                active_color=ColorPairs.BLACK_ON_BLUE,
                value=self.state.meta.convert_to_wav,
            ),
            "save": Button(self.window, "Save", 2, 10, active_color=ColorPairs.BLACK_ON_BLUE),
        }

    def get_placement(self, parent):
        return CenteredPanelPlacement(parent=parent, width=80, height=15)

    def on_element_keypress(self, elem_key, element, key):
        if elem_key == "save" and key.c in (curses.ascii.SP, curses.ascii.NL):
            convert_to_wav = self.elements["convert_to_wav"].get_value()
            self.db.meta_adapter.update(self.state.meta, convert_to_wav=convert_to_wav)
            if convert_to_wav:
                sounds = self.db.sound_adapter.list(path=NotLike("%.wav"))
                self.phase = Phase.CONVERT_TO_WAV

                if sounds:
                    self.redraw(force=True)
                    for idx, sound in enumerate(sounds):
                        self.set_line(x=3, y=4, text=f"[{idx + 1}/{len(sounds)}] {sound.name}")
                        self.redraw()
                        self.db.copy_sound_to_wav(sound)

            return False

        return super().on_element_keypress(elem_key, element, key)

    def take(self, key):
        if not self.state.is_popup_open and key.meta and key.s.lower() == "s":
            self.phase = Phase.CHANGE_SETTINGS
            self.window.clear()
            self.show()
            return True
        return super().take(key)
