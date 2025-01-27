from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from soundboard_fuck.data.category import Category
    from soundboard_fuck.data.sound import Sound


class SelectedObject:
    def __init__(self, idx: int, obj: "Sound | Category"):
        self.idx = idx
        self.obj = obj
