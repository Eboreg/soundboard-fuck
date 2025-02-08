import curses
import curses.ascii
from abc import ABC, abstractmethod

from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.elements.form_element import FormElement
from soundboard_fuck.ui.base.panels.base_panel import BasePanel
from soundboard_fuck.utils import step_dict


class BaseFormPanel(BasePanel, ABC):
    elements: dict[str, FormElement]
    element_idx: int = 0
    element_key: str

    @abstractmethod
    def create_elements(self) -> dict[str, FormElement]:
        ...

    def _rotate_element(self, step: int):
        elements = {k: v for k, v in self.get_elements().items() if not v.is_disabled}
        self.element_key = step_dict(elements, self.element_key, step)

    def contents(self):
        super().contents()
        for element in self.get_elements().values():
            element.draw()

    def get_elements(self) -> dict[str, FormElement]:
        return self.elements

    def loop(self):
        while True:
            elements = self.get_elements()
            if elements:
                element_key = self.element_key
                element = elements[element_key]
                key = element.activate()

                if key.c in (curses.KEY_DOWN, curses.ascii.TAB):
                    self._rotate_element(1)
                elif key.c in (curses.KEY_UP, curses.KEY_BTAB):
                    self._rotate_element(-1)
                elif key.c == curses.ascii.ESC:
                    break
                elif not self.on_element_keypress(element_key, element, key):
                    break
            else:
                return

        elements = self.get_elements()
        for element in elements.values():
            element.error = None
        self.element_key = list(elements.keys())[0]
        self.hide()

    def on_element_keypress(self, elem_key: str, element: FormElement, key: KeyPress) -> bool:
        """Return True to continue loop, False to break (and self.hide())"""
        return True

    def set_active_element(self, elem_key: str):
        self.element_key = elem_key

    def show(self):
        self.elements = self.create_elements()
        self.element_key = list(self.elements.keys())[0]
        super().show()
        self.loop()

    def take(self, key):
        if self.is_visible:
            if key.c == curses.ascii.ESC:
                self.hide()
            return True
        return super().take(key)
