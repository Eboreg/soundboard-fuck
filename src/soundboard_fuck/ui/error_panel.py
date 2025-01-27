from soundboard_fuck import log_handler
from soundboard_fuck.ui.base.panel import Panel


class ErrorPanel(Panel):
    def setup(self):
        log_handler.set_panel(self)
        self.window.scrollok(True)
        self.window.idlok(True)

    def contents(self):
        ...
