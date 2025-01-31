import curses
import curses.ascii
import time
from soundboard_fuck.keypress import KeyPress
from soundboard_fuck.ui.base.form_element import FormElement


class Timer(FormElement[None]):
    window: curses.window
    x = 0
    y = 0
    value = None
    finished: bool = False

    def activate(self):
        while not self.finished:
            time.sleep(0.2)
        return KeyPress(curses.ascii.ESC)

    def draw(self, active=False):
        ...
