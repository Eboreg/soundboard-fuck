from soundboard_fuck.db.abstractdb import AbstractDb
from soundboard_fuck.db.dummy.category_adapter import CategoryAdapter
from soundboard_fuck.db.dummy.meta_adapter import MetaAdapter
from soundboard_fuck.db.dummy.sound_adapter import SoundAdapter


class DummyDb(AbstractDb):
    sound_adapter: SoundAdapter
    category_adapter: CategoryAdapter
    meta_adapter: MetaAdapter

    def __init__(self):
        super().__init__()
        self.category_adapter = CategoryAdapter(self)
        self.sound_adapter = SoundAdapter(self)
        self.meta_adapter = MetaAdapter(self)

    def filter_sounds(self, query):
        return [s for s in self.sound_adapter.records if query.lower() in s.name.lower()]

    def list_categories(self):
        return self.category_adapter.list()

    def list_sounds(self):
        return self.sound_adapter.list()

    def set_default_category(self, category_id):
        for category in self.category_adapter.records:
            if category.id == category_id:
                category.is_default = True
            else:
                category.is_default = False
