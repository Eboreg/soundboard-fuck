from abc import ABC
from typing import Any

from soundboard_fuck.db.abstractdb import AbstractDb
from soundboard_fuck.state import State
from soundboard_fuck.ui.base.panels.base_panel import BasePanel


class AbstractPanel(BasePanel, ABC):
    def __init__(self, state: State, db: AbstractDb, border=None, z_index=None, create_hidden=None, is_popup=None):
        self.state = state
        self.db = db
        super().__init__(border, z_index, create_hidden, is_popup)
        self.state.add_listener(self.on_state_change)

    def on_state_change(self, name: str, value: Any):
        ...
