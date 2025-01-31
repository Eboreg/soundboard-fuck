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

    def _rotate_element(self, step: int):
        if abs(step) > len(self.elements):
            step = step % len(self.elements) if step >= 0 else step % (len(self.elements) * -1)
        if self.element_idx + step >= len(self.elements):
            self.element_idx = step - (len(self.elements) - self.element_idx)
        elif self.element_idx + step < 0:
            self.element_idx = len(self.elements) + step
        else:
            self.element_idx += step

    def get_elements(self) -> dict[str, FormElement]:
        return self.elements

    def loop(self):
        while True:
            elements = list(self.get_elements().items())
            if elements:
                elem_key, element = elements[self.element_idx]
                key = element.activate()

                if (
                    key.c in (curses.KEY_DOWN, curses.ascii.TAB) or
                    (isinstance(element, Input) and key.c == curses.ascii.NL)
                ):
                    self._rotate_element(1)
                elif key.c in (curses.KEY_UP, curses.KEY_BTAB):
                    self._rotate_element(-1)
                elif key.c == curses.ascii.ESC:
                    break
                elif not self.on_element_keypress(elem_key, element, key):
                    break
            else:
                return

        for element in self.elements.values():
            element.error = None
        self.element_idx = 0
        self.hide()

    def contents(self):
        super().contents()
        for element in self.get_elements().values():
            element.draw()

    @abstractmethod
    def create_elements(self) -> dict[str, FormElement]:
        ...

    def on_element_keypress(self, elem_key: str, element: FormElement, key: KeyPress) -> bool:
        """Return True to continue loop, False to break (and self.hide())"""
        return True

    def show(self):
        self.elements = self.create_elements()
        super().show()
        self.loop()

    def take(self, key):
        if not self.panel.hidden():
            if key.c == curses.ascii.ESC:
                self.hide()
            return True
        return super().take(key)
