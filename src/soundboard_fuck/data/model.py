from abc import ABC
from typing import TypeVar


class Model(ABC):
    id: int | None


_M = TypeVar("_M", bound=Model)
