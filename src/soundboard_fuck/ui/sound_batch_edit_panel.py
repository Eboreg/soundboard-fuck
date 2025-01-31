import curses
import curses.ascii

from soundboard_fuck.db.abstractdb import AbstractDb
from soundboard_fuck.state import State
from soundboard_fuck.ui import colors
from soundboard_fuck.ui.abstract_panel import AbstractPanel
from soundboard_fuck.ui.base.button import Button
from soundboard_fuck.ui.base.form_panel import FormPanel
from soundboard_fuck.ui.base.panel_placement import CenteredPanelPlacement
from soundboard_fuck.ui.category_select import CategorySelect


class SoundBatchEditPanel(FormPanel, AbstractPanel):
    create_hidden = True
    border = True
    title = "Edit sounds"

    def __init__(self, state: State, db: AbstractDb, z_index=None):
        self.db = db
        super().__init__(state=state, border=True, z_index=z_index)

    def create_elements(self):
        return {
            "category": CategorySelect(
                parent=self.window,
                x=2,
                y=1,
                inactive_color=colors.DARK_GRAY_ON_DEFAULT,
                selected_color=colors.BLACK_ON_BLUE,
                options=self.state.list_categories(),
            ),
            "button": Button(
                parent=self.window,
                x=2,
                y=4,
                label="Save",
                active_color=colors.BLACK_ON_BLUE,
            ),
        }

    def get_placement(self, parent):
        return CenteredPanelPlacement(parent=parent, width=40, height=8)

    def on_element_keypress(self, elem_key, element, key):
        if key.c == curses.KEY_RESIZE:
            self.state.on_resize()
            return True
        if elem_key == "button" and key.c in (curses.ascii.SP, curses.ascii.NL):
            for sound in self.state.selected_sounds:
                self.db.sound_adapter.update(sound, category_id=self.elements["category"].get_value().id)
            return False
        return True

    def take(self, key):
        if key.meta and key.s == "e" and self.state.selected_sounds:
            self.show()
            return True
        return False
