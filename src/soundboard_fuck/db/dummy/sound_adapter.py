from soundboard_fuck.data.sound import Sound, get_test_sounds
from soundboard_fuck.db.dummy.adapter import DummyAdapter


class SoundAdapter(DummyAdapter[Sound]):
    table_name = "sounds"

    def __init__(self, db):
        super().__init__(db)
        self.records = get_test_sounds(category_id=0)
