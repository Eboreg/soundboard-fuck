from soundboard_fuck.data.meta import Meta
from soundboard_fuck.db.dummy.adapter import DummyAdapter


class MetaAdapter(DummyAdapter[Meta]):
    table_name = "meta"

    def insert(self, record):
        self.records = []
        return super().insert(record)
