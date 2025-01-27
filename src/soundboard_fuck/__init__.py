import logging
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from soundboard_fuck.ui.error_panel import ErrorPanel


class LogHandler(logging.Handler):
    panel: "ErrorPanel | None" = None
    cache: list[logging.LogRecord]

    def __init__(self, level = logging.NOTSET):
        self.cache = []
        super().__init__(level)

    def emit(self, record):
        if self.panel:
            self.panel.window.addstr(record.getMessage() + "\n")
            self.panel.show()
        else:
            self.cache.append(record)

    def set_panel(self, panel: "ErrorPanel"):
        self.panel = panel
        for record in self.cache:
            self.emit(record)
        self.cache = []


log_handler = LogHandler()
logging.basicConfig(handlers=[log_handler], level=logging.INFO)
