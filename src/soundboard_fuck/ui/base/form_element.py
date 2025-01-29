import curses
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from soundboard_fuck.keypress import KeyPress


_T = TypeVar("_T")


class FormElement(ABC, Generic[_T]):
    parent: curses.window
    x: int
    y: int
    value: _T
    error: str | None = None

    @abstractmethod
    def activate(self) -> KeyPress:
        ...

    @abstractmethod
    def draw(self, active: bool = False):
        ...
