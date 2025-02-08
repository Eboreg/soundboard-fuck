import curses.ascii
from typing import TypedDict

from soundboard_fuck.data.category import Category
from soundboard_fuck.data.sound import Sound
from soundboard_fuck.ui.base.elements.button import Button
from soundboard_fuck.ui.base.elements.input import Input
from soundboard_fuck.ui.base.panel_placement import CenteredPanelPlacement
from soundboard_fuck.ui.category_select import CategorySelect
from soundboard_fuck.ui.colors import ColorPairs
from soundboard_fuck.ui.panels.form_panel import FormPanel


class Elements(TypedDict):
    name: Input
    category: CategorySelect
    save: Button
    delete: Button


class SoundEditPanel(FormPanel):
    create_hidden = True
    border = True
    sound: Sound
    title = "Edit sound"
    category: Category
    is_popup = True
    elements: Elements

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
                inactive_color=ColorPairs.DARK_GRAY_ON_DEFAULT,
                validator=self.validate_name,
                error_color=ColorPairs.RED_ON_DEFAULT,
                value=self.sound.name,
            ),
            "category": CategorySelect(
                parent=self.window,
                x=half_width + 3,
                y=1,
                inactive_color=ColorPairs.DARK_GRAY_ON_DEFAULT,
                selected_color=ColorPairs.BLACK_ON_BLUE,
                value=[c for c in categories if c.id == self.sound.category_id][0],
                options=categories,
            ),
            "save": Button(
                parent=self.window,
                x=2,
                y=4,
                label="Save",
                active_color=ColorPairs.BLACK_ON_BLUE,
            ),
            "delete": Button(
                parent=self.window,
                x=10,
                y=4,
                label="Delete",
                active_color=ColorPairs.BLACK_ON_RED,
            )
        }

    def get_placement(self, parent):
        return CenteredPanelPlacement(parent=parent, width=80, height=8)

    def on_element_keypress(self, elem_key, element, key):
        if key.c in (curses.ascii.SP, curses.ascii.NL):
            if elem_key == "save":
                if not self.elements["name"].error:
                    self.db.sound_adapter.update(
                        self.sound,
                        name=self.elements["name"].get_value(),
                        category_id=self.elements["category"].get_value().id,
                    )
                    return False
            if elem_key == "delete":
                self.db.sound_adapter.delete(id=self.sound.id)
                return False
        return super().on_element_keypress(elem_key, element, key)

    def take(self, key):
        if (
            not self.state.is_popup_open and
            key.meta and
            key.s == "e" and
            self.state.selected_sound and
            not self.state.selected_sounds
        ):
            self.sound = self.state.selected_sound
            self.show()
            return True
        return super().take(key)

    def validate_name(self, value: str):
        if value == "":
            return "Cannot be empty."
        return None
