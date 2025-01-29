import curses
import curses.ascii
from abc import ABC, abstractmethod

from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.form_element import FormElement
from soundboard_fuck.ui.base.input import Input
from soundboard_fuck.ui.base.panel import Panel


class FormPanel(Panel, ABC):
    elements: dict[str, FormElement]
    element_idx: int = 0

    def activate(self):
        elem_key, element = list(self.elements.items())[self.element_idx]
        key = element.activate()
        if key.c in (curses.KEY_DOWN, curses.ascii.TAB) or (isinstance(element, Input) and key.c == curses.ascii.NL):
            self.activate_next()
        elif key.c in (curses.KEY_UP, curses.KEY_BTAB):
            self.activate_previous()
        elif key.c == curses.ascii.ESC:
            self.hide()
        else:
            self.on_element_keypress(elem_key, element, key)

    def activate_next(self):
        self.element_idx = self.element_idx + 1 if self.element_idx < len(self.elements) - 1 else 0
        self.activate()

    def activate_previous(self):
        self.element_idx = self.element_idx - 1 if self.element_idx > 0 else len(self.elements) - 1
        self.activate()

    def contents(self):
        for element in self.elements.values():
            element.draw()

    @abstractmethod
    def create_elements(self) -> dict[str, FormElement]:
        ...

    def on_element_keypress(self, elem_key: str, element: FormElement, key: KeyPress):
        ...

    def setup(self):
        super().setup()
        self.elements = self.create_elements()

    def show(self):
        super().show()
        self.activate()
