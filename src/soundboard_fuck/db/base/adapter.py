from abc import ABC, abstractmethod
from typing import Generic

from soundboard_fuck.data.model import _M


class DbAdapter(Generic[_M], ABC):
    table_name: str

    @abstractmethod
    def bulk_insert(self, records: list[_M]):
        ...

    @abstractmethod
    def delete(self, **where):
        ...

    @abstractmethod
    def get(self, columns: list[str] | None = None, **where) -> _M:
        ...

    @abstractmethod
    def insert(self, record: _M) -> _M:
        ...

    @abstractmethod
    def list(self, order_by: list[str] | None = None, columns: list[str] | None = None, **where) -> list[_M]:
        ...

    @abstractmethod
    def update(self, record: _M, **changes) -> bool:
        ...
