from copy import deepcopy

from soundboard_fuck.data.category import Category, test_categories
from soundboard_fuck.data.sound import Sound, get_test_sounds
from soundboard_fuck.db.abstractdb import AbstractDb
from soundboard_fuck.enums import RepressMode


class DummyDb(AbstractDb):
    _categories: "dict[int, Category]"
    _sounds: "dict[int, Sound]"
    _repress_mode = RepressMode.STOP

    @property
    def categories(self):
        for c in self._categories.values():
            sounds = [s for s in self._sounds.values() if s.category_id == c.id]
            c.sound_count = len(sounds)
            c.duration_ms = sum((s.duration_ms for s in sounds if s.duration_ms), start=0)
        return self._categories

    def __init__(self):
        super().__init__()
        self._categories = {c.id: deepcopy(c) for c in test_categories}
        self._sounds = {s.id: deepcopy(s) for s in get_test_sounds(0)}

    def create_category(self, name, order, colors, is_expanded):
        max_id = max(*self._categories.keys(), 0)
        category = Category(
            id=max_id + 1,
            name=name,
            order=order,
            colors=colors,
            is_expanded=is_expanded,
            sound_count=0,
            duration_ms=0,
            is_default=False,
        )
        self._categories[category.id] = category
        self.notify_listeners("categories")
        return category

    def create_sound(self, name, path, category_id = None, duration_ms = None):
        max_id = max(*self._sounds.keys(), 0)
        category = self.get_category(category_id)
        sound = Sound(
            id=max_id + 1,
            name=name,
            path=path,
            category_id=category_id,
            duration_ms=duration_ms,
            colors=category.colors,
        )
        self._sounds[sound.id] = sound
        self.notify_listeners("sounds")
        return sound

    def delete_category(self, category_id):
        try:
            del self._categories[category_id]
            self.notify_listeners("categories")
        except NameError:
            pass

    def delete_sound(self, sound_id):
        try:
            del self._sounds[sound_id]
            self.notify_listeners("sounds")
        except NameError:
            pass

    def filter_sounds(self, query):
        return [s for s in self._sounds.values() if query.lower() in s.name.lower()]

    def get_category(self, category_id):
        return self.categories[category_id]

    def get_repress_mode(self):
        return self._repress_mode

    def get_sound(self, sound_id):
        return self._sounds[sound_id]

    def list_categories(self):
        return list(self.categories.values())

    def list_sounds(self):
        return list(self._sounds.values())

    def save_categories(self, *categories):
        if categories:
            for category in categories:
                self._categories[category.id] = category
            self.notify_listeners("categories")

    def save_sounds(self, *sounds):
        if sounds:
            for sound in sounds:
                self._sounds[sound.id] = sound
            self.notify_listeners("sounds")

    def set_default_category(self, category_id):
        for category in self._categories.values():
            if category.id == category_id:
                category.is_default = True
            else:
                category.is_default = False

    def set_repress_mode(self, value):
        self._repress_mode = value
        self.notify_listeners("meta")
