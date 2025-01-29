from abc import ABC
from typing import Any

from soundboard_fuck.state import State
from soundboard_fuck.ui.base.panel import Panel


class AbstractPanel(Panel, ABC):
    def __init__(self, state: State, border = None, z_index = None):
        super().__init__(border, z_index)
        self.state = state
        self.state.on_change(self.on_state_change)

    def on_state_change(self, name: str, value: Any):
        ...
