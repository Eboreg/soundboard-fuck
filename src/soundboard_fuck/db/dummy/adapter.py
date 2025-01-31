from typing import TYPE_CHECKING

from abc import ABC
from soundboard_fuck.data.model import _M
from soundboard_fuck.db.base.adapter import DbAdapter


if TYPE_CHECKING:
    from soundboard_fuck.db.dummydb import DummyDb


class DummyAdapter(DbAdapter[_M], ABC):
    records: "list[_M]"

    def __init__(self, db: "DummyDb"):
        self.db = db
        self.records = []
        super().__init__()

    def bulk_insert(self, records: list[_M]):
        self.records += records
        self.db.notify_listeners(self.table_name)

    def delete(self, **where):
        for r in self.records:
            if all(getattr(r, k) == v for k, v in where.items()):
                self.records -= r
        self.db.notify_listeners(self.table_name)

    def get(self, columns: list[str] | None = None, **where) -> _M:
        return [r for r in self.records if all(getattr(r, k) == v for k, v in where.items())][0]

    def insert(self, record: _M) -> _M:
        self.records += record
        self.db.notify_listeners(self.table_name)

    def list(self, order_by: list[str] | None = None, columns: list[str] | None = None, **where) -> list[_M]:
        records = [r for r in self.records if all(getattr(r, k) == v for k, v in where.items())]
        if order_by:
            return sorted(records, key=lambda r: getattr(r, order_by[0]))
        return records

    def update(self, record: _M, **changes) -> bool:
        changes = {k: v for k, v in changes.items() if getattr(record, k) != v}
        if changes:
            for k, v in changes.items():
                setattr(record, k, v)
            for r in self.records:
                if r.id == record.id:
                    self.records.remove(r)
                    break
            self.records += record
            self.db.notify_listeners(self.table_name)
            return True
        return False
