from soundboard_fuck.data.category import Category
from soundboard_fuck.db.abstractdb import AbstractDb
from soundboard_fuck.state import State
from soundboard_fuck.ui.abstract_panel import AbstractPanel


class SoundBatchEditPanel(AbstractPanel):
    def __init__(self, state: State, db: AbstractDb, z_index = 0):
        self.db = db
        super().__init__(state=state, border=True, z_index=z_index)

    @property
    def categories(self) -> list[Category]:
        return [cws.category for cws in self.state.categories_with_sounds if cws.category]

    def contents(self):
        self.set_line(0, 0, "Select a category:")
        for idx, cat in enumerate(self.categories):
            self.set_line(0, 2 + idx, f"{idx}. {cat.name}")

    def on_state_change(self, name, value):
        if name == "show_sound_batch_edit":
            if value is True:
                self.show()
            else:
                self.hide()

    def take(self, key):
        if key.escape and self.state.show_sound_batch_edit:
            self.state.show_sound_batch_edit = False
            return True
        if key.meta and key.s == "e" and self.state.selected_sounds:
            self.state.show_sound_batch_edit = True
            return True
        if self.state.show_sound_batch_edit and not key.escape and not key.ctrl and not key.meta:
            try:
                idx = int(key.s)
                if idx < len(self.categories):
                    category = self.categories[idx]
                    for sound in self.state.selected_sounds:
                        sound.category_id = category.id
                    self.db.save_sounds(*self.state.selected_sounds)
                    self.state.show_sound_batch_edit = False
                    return True
            except ValueError:
                pass
        return super().take(key)
