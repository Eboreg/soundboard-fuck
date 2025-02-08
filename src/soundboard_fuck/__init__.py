import logging
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from soundboard_fuck.ui.panels.error_panel import ErrorPanel


class LogHandler(logging.StreamHandler):
    panel: "ErrorPanel | None" = None
    cache: list[logging.LogRecord]

    def __init__(self, stream = None):
        self.cache = []
        super().__init__(stream)

    def emit(self, record):
        if self.panel:
            self.panel.window.addstr(record.getMessage().strip() + "\n")
            self.panel.show()
        else:
            self.cache.append(record)
            super().emit(record)

    def set_panel(self, panel: "ErrorPanel"):
        self.panel = panel
        for record in self.cache:
            self.emit(record)
        self.cache = []

    def write(self, data):
        if data:
            self.emit(logging.makeLogRecord({"level": logging.ERROR, "msg": str(data)}))


log_handler = LogHandler()
logging.basicConfig(handlers=[log_handler], level=logging.INFO)
