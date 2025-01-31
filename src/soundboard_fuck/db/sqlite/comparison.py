from abc import ABC
from dataclasses import dataclass
from typing import Any


class Comparison(ABC):
    value: Any


@dataclass
class Equals(Comparison):
    value: Any
    quote: bool = True

    def __str__(self):
        if self.quote:
            return f" = '{self.value}'"
        return f" = {self.value}"


@dataclass
class Like(Comparison):
    value: Any

    def __str__(self):
        return f" LIKE '{self.value}'"


@dataclass
class NotLike(Comparison):
    value: Any

    def __str__(self):
        return f" NOT LIKE '{self.value}'"
