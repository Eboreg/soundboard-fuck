from soundboard_fuck.data.category import Category, test_categories
from soundboard_fuck.db.dummy.adapter import DummyAdapter


class CategoryAdapter(DummyAdapter[Category]):
    table_name = "categories"

    def __init__(self, db):
        super().__init__(db)
        self.records = test_categories

    def insert(self, record):
        for r in self.records:
            if r.order >= record.order:
                r.order += 1
        return super().insert(record)

    def update(self, record, **changes):
        if any(r for r in self.records if r.id != record.id and r.order == record.order):
            for r in self.records:
                if r.order >= record.order:
                    r.order += 1
        return super().update(record, **changes)
