import curses
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any

from pyaudio import PyAudio

from soundboard_fuck.data.category import Category
from soundboard_fuck.data.sound import Sound
from soundboard_fuck.data.soundlist import SoundList
from soundboard_fuck.db.abstractdb import AbstractDb
from soundboard_fuck.enums import RepressMode
from soundboard_fuck.player.wavplayer import WavPlayer
from soundboard_fuck.progress_collection import ProgressCollection
from soundboard_fuck.ui.abstract_panel import AbstractPanel
from soundboard_fuck.utils import coerce_at_least, coerce_between


if TYPE_CHECKING:
    from soundboard_fuck.keypress import KeyPress
    from soundboard_fuck.player.abstractplayer import AbstractPlayer
    from soundboard_fuck.player.playerprogress import PlayerProgress
    from soundboard_fuck.state import State


class SoundPanel(AbstractPanel):
    sounds: SoundList
    executor: ThreadPoolExecutor
    currently_playing: "list[AbstractPlayer]"
    pyaudio: PyAudio
    progresses: ProgressCollection

    def __init__(self, state: "State", db: AbstractDb, border = False, z_index = 0):
        super().__init__(state=state, border=border, z_index=z_index)
        self.db = db
        self.sounds = SoundList(
            categories_with_sounds=self.state.categories_with_sounds,
            on_selected_change=self._on_selected_change,
        )
        self.currently_playing = []
        self.progresses = ProgressCollection()
        self.pyaudio = PyAudio()
        self.executor = ThreadPoolExecutor(max_workers=10)

    @property
    def max_y(self) -> int:
        return self.window.getmaxyx()[0]

    @property
    def selected_object(self) -> "Sound | Category | None":
        selected = self.sounds.selected
        if selected:
            return selected.obj
        return None

    def _color_pair(self, pair_number: int) -> int | None:
        if curses.has_colors():
            return curses.color_pair(pair_number)
        return None

    def _is_playing(self, sound_id: int) -> bool:
        return len([p for p in self.currently_playing if p.sound.id == sound_id]) > 0

    def _move_to_idx(self, new_idx: int, old_idx: int | None = None):
        new_idx = coerce_at_least(new_idx, 0)
        indices = self.sounds.move_to_idx(new_idx, self.max_y, old_idx=old_idx)
        if indices:
            selected = self.selected_object
            for idx in indices:
                obj = self.sounds.get_object_at_idx(idx)
                pos = self.sounds.idx_to_pos(idx)
                self._render_object_at_pos(pos=pos, obj=obj, selected=selected == obj)
            self.redraw()

    def _on_enter_press(self):
        selected = self.selected_object
        if isinstance(selected, Sound):
            if self.state.selected_sounds:
                if selected in self.state.selected_sounds:
                    self.state.selected_sounds = self.state.selected_sounds.difference({selected})
                else:
                    self.state.selected_sounds = self.state.selected_sounds.union({selected})
                self._step_single(1)
            elif self._is_playing(selected.id):
                if self.state.repress_mode == RepressMode.STOP:
                    self._stop_sound(selected.id)
                elif self.state.repress_mode == RepressMode.OVERDUB:
                    self._play_sound(selected)
                elif self.state.repress_mode == RepressMode.RESTART:
                    self._stop_sound(selected.id)
                    self._play_sound(selected)
            else:
                self._play_sound(selected)

    def _on_progress(self, progress: "PlayerProgress"):
        if self.progresses.append(progress):
            pos = self.sounds.get_sound_pos_if_visible(progress.sound_id, self.max_y)
            if pos is not None:
                self._render_progress(pos, progress.progress)
                self.redraw()

    def _on_selected_change(self, obj: "Sound | Category | None"):
        if isinstance(obj, Sound):
            self.state.selected_sound_id = obj.id
            self.state.selected_category_id = None
        elif isinstance(obj, Category):
            self.state.selected_category_id = obj.id
            self.state.selected_sound_id = None

    def _on_stop(self, player: "AbstractPlayer"):
        try:
            self.currently_playing.remove(player)
        except ValueError:
            pass
        if self.progresses.delete(player):
            try:
                idx, obj = self.sounds.find(player.sound)
                if idx in self.sounds.get_visible_indices(self.max_y):
                    self._render_object_at_pos(
                        pos=self.sounds.idx_to_pos(idx),
                        obj=obj,
                        selected=obj == self.selected_object,
                    )
                    self.redraw()
            except ValueError:
                pass
        if player.progress >= 0.5:
            sound = player.sound.copy(play_count=player.sound.play_count + 1)
            self.db.save_sounds(sound)

    def _play_sound(self, sound: "Sound"):
        player = WavPlayer(sound=sound, p=self.pyaudio, on_stop=self._on_stop, on_progress=self._on_progress)
        self.currently_playing.append(player)
        self.executor.submit(player.play)

    def _render_progress(self, pos: int, progress: float):
        stars = "█" * round(progress * 20)
        self.window.addstr(pos, 30, stars)
        if len(stars) < 20:
            filler = "░" * (20 - len(stars))
            self.window.addstr(pos, 30 + len(stars), filler)

    def _render_object_at_pos(self, pos: int, obj: "Sound | Category | None", selected: bool):
        if obj:
            attr = (
                self._color_pair(obj.colors.value.selected) if selected
                else self._color_pair(obj.colors.value.regular)
            )
            text = obj.name

            if isinstance(obj, Category):
                text = f"[ {obj.name} ]"
                attr |= curses.A_BOLD
            else:
                if obj in self.state.selected_sounds:
                    attr |= curses.A_BOLD
                    text = f" * {text}"
                else:
                    attr |= curses.A_NORMAL

            self.set_line(0, pos, text, attr=attr)

            if isinstance(obj, Sound):
                progress = self.progresses.get_sound_progress(obj.id)
                if progress is not None:
                    self._render_progress(pos, progress)
        else:
            self.clear_line(0, pos)

    def _step_page(self, pages: int):
        old_idx = self.sounds.selected_idx or 0
        new_idx = old_idx + (pages * (self.max_y - 1))
        new_idx = coerce_between(new_idx, 0, coerce_at_least(len(self.sounds) - 1, 0))
        self._move_to_idx(new_idx, old_idx)

    def _step_single(self, steps: int):
        old_idx = self.sounds.selected_idx or 0
        new_idx = old_idx + steps

        if new_idx < 0:
            new_idx = len(self.sounds) - 1
        elif new_idx >= len(self.sounds):
            new_idx = 0

        self._move_to_idx(new_idx, old_idx)

    def _stop_sound(self, sound_id: int):
        for player in [p for p in self.currently_playing if p.sound.id == sound_id]:
            player.stop()

    def contents(self):
        selected = self.sounds.selected
        self.sounds.update_offset(self.max_y, selected.idx if selected else None)
        for pos in range(self.max_y):
            idx = pos + self.sounds.offset
            obj = self.sounds.get_object_at_idx(idx)
            self._render_object_at_pos(pos=pos, obj=obj, selected=selected and selected.obj == obj)

    def on_state_change(self, name: str, value: Any):
        if name == "selected_sounds":
            self.redraw(force=True)
        elif name == "categories_with_sounds":
            explicitly_selected = self.sounds.explicitly_selected
            self.sounds = SoundList(
                categories_with_sounds=value,
                explicitly_selected=explicitly_selected,
                on_selected_change=self._on_selected_change,
            )
            self.redraw(force=True)

    def stop_all(self):
        for player in self.currently_playing:
            player.stop()

    def take(self, key: "KeyPress") -> bool:
        accepted_c = [
            curses.KEY_DOWN,
            curses.KEY_UP,
            curses.KEY_NPAGE,
            curses.KEY_PPAGE,
            curses.KEY_HOME,
            curses.KEY_END,
        ]
        accepted_s = ["\n"]

        if key.meta:
            if key.s == "s":
                self.stop_all()
                return True
            return False

        if key.ctrl and key.c == 0:
            # ctrl+space activates/deactivates sound selection
            if self.state.selected_sounds:
                self.state.selected_sounds = set()
            elif isinstance(self.selected_object, Sound):
                self.state.selected_sounds = self.state.selected_sounds.union({self.selected_object})
                self._step_single(1)
            return True

        if key.c in accepted_c or key.s in accepted_s:
            if key.c == curses.KEY_DOWN:
                self._step_single(1)
            elif key.c == curses.KEY_UP:
                self._step_single(-1)
            elif key.c == curses.KEY_NPAGE:
                self._step_page(1)
            elif key.c == curses.KEY_PPAGE:
                self._step_page(-1)
            elif key.c == curses.KEY_HOME:
                self._move_to_idx(0)
            elif key.c == curses.KEY_END:
                self._move_to_idx(len(self.sounds) - 1)
            elif key.s == "\n":
                self._on_enter_press()
            return True

        return False
