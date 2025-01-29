from typing import Any, Callable

from soundboard_fuck.data.category import Category
from soundboard_fuck.data.category_with_sounds import CategoryWithSounds
from soundboard_fuck.data.sound import Sound
from soundboard_fuck.selected_object import SelectedObject


class SoundList:
    explicitly_selected: SelectedObject | None = None
    offset: int = 0
    objects: list[Sound | Category]

    def __init__(
        self,
        categories_with_sounds: list[CategoryWithSounds],
        on_selected_change: Callable[[Sound | Category | None], Any],
        explicitly_selected: SelectedObject | None = None,
        offset: int | None = None,
    ):
        self.objects = []
        if offset is not None:
            self.offset = offset
        for cws in categories_with_sounds:
            if cws.category:
                self.objects.append(cws.category)
            if not cws.category or cws.category.is_expanded:
                self.objects.extend(cws.sounds)
        self.on_selected_change = on_selected_change
        if explicitly_selected:
            self.explicitly_selected = explicitly_selected
        if explicitly_selected and explicitly_selected.obj in self.objects:
            self.on_selected_change(explicitly_selected.obj)
        else:
            selected = self.selected
            if selected:
                self.on_selected_change(selected.obj)
            else:
                self.on_selected_change(None)

    def __getitem__(self, key: int):
        return self.objects[key]

    def __len__(self):
        return len(self.objects)

    @property
    def selected(self) -> SelectedObject | None:
        if self.objects:
            if self.explicitly_selected:
                try:
                    idx, obj = self.find(self.explicitly_selected.obj)
                    return SelectedObject(idx, obj)
                except ValueError:
                    pass
            return SelectedObject(0, self.objects[0])
        return None

    @property
    def selected_idx(self) -> int | None:
        selected = self.selected
        return selected.idx if selected else None

    def _change_selected(self, new_idx: int):
        if self.objects:
            obj = self.objects[new_idx]
            self.explicitly_selected = SelectedObject(new_idx, obj)
            self.on_selected_change(obj)

    def copy(
        self,
        categories_with_sounds: list[CategoryWithSounds],
        on_selected_change: Callable[[Sound | Category | None], Any],
    ):
        return SoundList(
            categories_with_sounds=categories_with_sounds,
            explicitly_selected=self.explicitly_selected,
            on_selected_change=on_selected_change,
            offset=self.offset,
        )

    def find(self, obj: Sound | Category) -> tuple[int, Sound | Category]:
        for idx, o in enumerate(self.objects):
            if obj.id == o.id:
                if isinstance(obj, Sound) and isinstance(o, Sound):
                    return idx, o
                if isinstance(obj, Category) and isinstance(o, Category):
                    return idx, o
        raise ValueError(f"{obj} is not in list")

    def get_object_at_idx(self, idx: int) -> Sound | Category | None:
        if 0 <= idx < len(self.objects):
            return self.objects[idx]
        return None

    def get_sound_pos_if_visible(self, sound_id: int, page_size: int) -> int | None:
        for idx, obj in enumerate(self.objects):
            if isinstance(obj, Sound) and obj.id == sound_id:
                if idx in self.get_visible_indices(page_size):
                    return self.idx_to_pos(idx)
                return None
        return None

    def get_visible_indices(self, page_size: int) -> range:
        # start=inclusive, end=exclusive
        return range(
            self.offset,
            min(self.offset + page_size, len(self.objects)),
        )

    def idx_to_pos(self, idx: int) -> int:
        return idx - self.offset

    def move_to_idx(self, new_idx: int, page_size: int, old_idx: int | None = None) -> set[int]:
        # Returns affected (visible) indices
        if old_idx is None:
            old_idx = self.selected_idx or 0

        if old_idx != new_idx:
            old_indices = list(self.get_visible_indices(page_size))
            self._change_selected(new_idx)
            self.update_offset(page_size, new_idx)
            new_indices = list(self.get_visible_indices(page_size))

            if new_indices != old_indices:
                return {*new_indices}
            return {old_idx, new_idx}

        return set()

    def update_offset(self, page_size: int, selected_idx: int | None = None):
        if selected_idx is None:
            selected_idx = self.selected_idx

        if len(self.objects) < page_size:
            self.offset = 0

        elif selected_idx is not None:
            indices = self.get_visible_indices(page_size)
            if selected_idx < indices.start:
                self.offset = selected_idx
            elif selected_idx >= indices.stop:
                self.offset = selected_idx - page_size + 1
