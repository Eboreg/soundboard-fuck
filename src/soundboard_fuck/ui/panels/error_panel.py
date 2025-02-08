from soundboard_fuck import log_handler
from soundboard_fuck.ui.panels.abstract_panel import AbstractPanel
from soundboard_fuck.ui.base.panel_placement import PanelPlacement


class ErrorPanel(AbstractPanel):
    create_hidden = True

    def get_placement(self, parent):
        return PanelPlacement(x=61, y=3, width=parent.width - 62, height=parent.height - 3, parent=parent)

    def setup(self):
        log_handler.set_panel(self)
        self.window.scrollok(True)
        self.window.idlok(True)
