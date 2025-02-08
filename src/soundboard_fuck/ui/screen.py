from typing import TYPE_CHECKING

from soundboard_fuck.data.sound import Sound, get_test_sounds
from soundboard_fuck.state import State
from soundboard_fuck.ui import colors
from soundboard_fuck.ui.panels.file_selection_panel import FileSelectionPanel
from soundboard_fuck.ui.base.screen import Screen
from soundboard_fuck.ui.panels.bottom_panel import BottomPanel
from soundboard_fuck.ui.panels.category_edit_panel import CategoryEditPanel
from soundboard_fuck.ui.panels.error_panel import ErrorPanel
from soundboard_fuck.ui.panels.help_panel import HelpPanel
from soundboard_fuck.ui.panels.settings_panel import SettingsPanel
from soundboard_fuck.ui.panels.sound_batch_edit_panel import SoundBatchEditPanel
from soundboard_fuck.ui.panels.sound_edit_panel import SoundEditPanel
from soundboard_fuck.ui.panels.sound_panel import SoundPanel
from soundboard_fuck.ui.panels.top_panel import TopPanel


if TYPE_CHECKING:
    from soundboard_fuck.db.abstractdb import AbstractDb


class SoundboardScreen(Screen):
    db: "AbstractDb"
    quit: bool = False
    state: State

    def __init__(self, db: "AbstractDb", border = False):
        super().__init__(border)
        self.db = db
        self.state = State(self.db, self)
        self.state.add_resize_listener(self.on_resize)

    def bootstrap_data(self):
        category = self.db.get_or_create_default_category()
        sounds = get_test_sounds(category.id)
        for sound in sounds:
            sound.duration_ms = Sound.extract_duration_ms(sound.path)
        self.db.sound_adapter.bulk_insert(sounds)

    def create_panels(self):
        return [
            CategoryEditPanel(state=self.state, db=self.db, z_index=2),
            SoundEditPanel(state=self.state, db=self.db, z_index=2),
            SoundBatchEditPanel(state=self.state, db=self.db, z_index=2),
            HelpPanel(state=self.state, db=self.db, z_index=2),
            TopPanel(state=self.state, db=self.db),
            SoundPanel(state=self.state, db=self.db),
            BottomPanel(state=self.state, db=self.db),
            ErrorPanel(state=self.state, db=self.db, z_index=1),
            SettingsPanel(state=self.state, db=self.db, z_index=2),
            FileSelectionPanel(state=self.state, db=self.db, z_index=2),
        ]

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
        super().setup()
