import curses.ascii

from soundboard_fuck.data.category import Category
from soundboard_fuck.data.sound import Sound
from soundboard_fuck.db.abstractdb import AbstractDb
from soundboard_fuck.ui import colors
from soundboard_fuck.ui.abstract_panel import AbstractPanel
from soundboard_fuck.ui.base.button import Button
from soundboard_fuck.ui.base.form_panel import FormPanel
from soundboard_fuck.ui.base.input import Input
from soundboard_fuck.ui.base.panel_placement import CenteredPanelPlacement
from soundboard_fuck.ui.category_select import CategorySelect


class SoundEditPanel(FormPanel, AbstractPanel):
    create_hidden = True
    border = True
    sound: Sound
    title = "Edit sound"
    category: Category

    def __init__(self, state, db: AbstractDb, border=None, z_index=None):
        self.db = db
        super().__init__(state, border, z_index)

    def create_elements(self):
        half_width = int(self.width / 2) - 1
        categories = self.state.list_categories()

        return {
            "name": Input(
                parent=self.window,
                x=2,
                y=1,
                label="Name",
                width=half_width,
                inactive_color=colors.DARK_GRAY_ON_DEFAULT,
                validator=self.validate_name,
                error_color=colors.RED_ON_DEFAULT,
                value=self.sound.name,
            ),
            "category": CategorySelect(
                parent=self.window,
                x=half_width + 3,
                y=1,
                inactive_color=colors.DARK_GRAY_ON_DEFAULT,
                selected_color=colors.BLACK_ON_BLUE,
                value=[c for c in categories if c.id == self.sound.category_id][0],
                options=categories,
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
        return CenteredPanelPlacement(parent=parent, width=80, height=8)

    def on_element_keypress(self, elem_key, element, key):
        if key.c == curses.KEY_RESIZE:
            self.state.on_resize()
            return True
        if elem_key == "button" and key.c in (curses.ascii.SP, curses.ascii.NL):
            if not self.elements["name"].error:
                self.db.sound_adapter.update(
                    self.sound,
                    name=self.elements["name"].value,
                    category_id=self.elements["category"].value.id,
                )
                return False
        return True

    def take(self, key):
        if key.meta and key.s == "e" and self.state.selected_sound and not self.state.selected_sounds:
            self.sound = self.state.selected_sound
            self.show()
            return True
        return super().take(key)

    def validate_name(self, value: str):
        if value == "":
            return "Cannot be empty."
        return None
