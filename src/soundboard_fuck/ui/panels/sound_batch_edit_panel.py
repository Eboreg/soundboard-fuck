import curses
import curses.ascii
from typing import TypedDict

from soundboard_fuck.db.sqlite.comparison import In
from soundboard_fuck.ui.base.elements.button import Button
from soundboard_fuck.ui.base.panel_placement import CenteredPanelPlacement
from soundboard_fuck.ui.category_select import CategorySelect
from soundboard_fuck.ui.colors import ColorPairs
from soundboard_fuck.ui.panels.form_panel import FormPanel


class Elements(TypedDict):
    category: CategorySelect
    save: Button
    delete: Button


class SoundBatchEditPanel(FormPanel):
    create_hidden = True
    border = True
    title = "Edit sounds"
    is_popup = True
    elements: Elements

    def create_elements(self):
        return {
            "category": CategorySelect(
                parent=self.window,
                x=2,
                y=1,
                inactive_color=ColorPairs.DARK_GRAY_ON_DEFAULT,
                selected_color=ColorPairs.BLACK_ON_BLUE,
                options=self.state.list_categories(),
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
            ),
        }

    def get_placement(self, parent):
        return CenteredPanelPlacement(parent=parent, width=40, height=8)

    def on_element_keypress(self, elem_key, element, key):
        if key.c in (curses.ascii.SP, curses.ascii.NL):
            if elem_key == "save":
                for sound in self.state.selected_sounds:
                    self.db.sound_adapter.update(sound, category_id=self.elements["category"].get_value().id)
                return False
            if elem_key == "delete":
                self.db.sound_adapter.delete(id=In([s.id for s in self.state.selected_sounds]))
                return False
        return super().on_element_keypress(elem_key, element, key)

    def take(self, key):
        if not self.state.is_popup_open and key.meta and key.s == "e" and self.state.selected_sounds:
            self.show()
            return True
        return False
