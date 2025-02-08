import curses
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar

from soundboard_fuck.keypress import KeyPress


_T = TypeVar("_T")


class FormElement(ABC, Generic[_T]):
    parent: curses.window
    x: int
    y: int
    error: str | None = None
    is_active: bool = False
    is_disabled: bool = False
    _value: _T

    def __init__(
        self,
        parent: curses.window,
        x: int | None = None,
        y: int | None = None,
        value: _T | None = None,
        validator: Callable[[_T], str | None] | None = None,
        on_change: Callable[[_T], Any] | None = None,
    ):
        self.parent = parent
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if value is not None:
            self._value = value
        self.validator = validator
        self.on_change = on_change

    @property
    def value_or_null(self) -> _T | None:
        if hasattr(self, "_value"):
            return self._value
        return None

    def set_value(self, value: _T, notify: bool = True):
        if not hasattr(self, "_value") or self._value != value:
            self._value = value
            self.error = self.validate(value)
            if self.on_change and notify:
                self.on_change(value)

    def activate(self) -> KeyPress:
        self.is_active = True
        self.draw()
        key = self.get_keypress()
        self.is_active = False
        self.draw()
        return key

    @abstractmethod
    def get_keypress(self) -> KeyPress:
        ...

    @abstractmethod
    def draw(self):
        ...

    def get_value(self) -> _T:
        return self._value

    def validate(self, value: _T) -> str | None:
        if self.validator:
            return self.validator(value)
        return None
