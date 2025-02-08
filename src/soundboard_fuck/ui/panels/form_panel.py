from abc import ABC
import curses
from soundboard_fuck.ui.panels.abstract_panel import AbstractPanel
from soundboard_fuck.ui.base.panels.base_form_panel import BaseFormPanel


class FormPanel(BaseFormPanel, AbstractPanel, ABC):
    def on_element_keypress(self, elem_key, element, key):
        if key.c == curses.KEY_RESIZE:
            self.state.on_resize()
            return True
        return super().on_element_keypress(elem_key, element, key)
