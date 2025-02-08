import curses
import curses.ascii
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any

from pyaudio import PyAudio

from soundboard_fuck.data.category import Category
from soundboard_fuck.data.sound import Sound
from soundboard_fuck.data.soundlist import SoundList
from soundboard_fuck.enums import RepressMode
from soundboard_fuck.player.wavplayer import WavPlayer
from soundboard_fuck.progress_collection import ProgressCollection
from soundboard_fuck.ui.panels.abstract_panel import AbstractPanel
from soundboard_fuck.ui.base.panel_placement import PanelPlacement
from soundboard_fuck.utils import (
    coerce_at_least,
    coerce_at_most,
    coerce_between,
    format_milliseconds,
)


if TYPE_CHECKING:
    from soundboard_fuck.keypress import KeyPress
    from soundboard_fuck.player.abstractplayer import AbstractPlayer
    from soundboard_fuck.player.playerprogress import PlayerProgress


class SoundPanel(AbstractPanel):
    sounds: SoundList
    executor: ThreadPoolExecutor
    currently_playing: "list[AbstractPlayer]"
    pyaudio: PyAudio
    progresses: ProgressCollection

    def __init__(self, state, db, border=None, z_index=None, create_hidden=None, is_popup=None):
        super().__init__(state, db, border, z_index, create_hidden, is_popup)
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

    def _is_playing(self, sound_id: int) -> bool:
        return len([p for p in self.currently_playing if p.sound.id == sound_id]) > 0

    def _move_to_idx(self, new_idx: int, old_idx: int | None = None):
        new_idx = coerce_at_least(new_idx, 0)
        indices = self.sounds.move_to_idx(new_idx, self.max_y, old_idx=old_idx)
        if indices:
            for idx in indices:
                obj = self.sounds.get_object_at_idx(idx)
                pos = self.sounds.idx_to_pos(idx)
                self._render_object_at_pos(pos=pos, obj=obj, selected=self.selected_object == obj)
            self._render_scrollbar()
            self.redraw()

    def _on_enter_press(self):
        selected = self.selected_object
        if isinstance(selected, Sound):
            if self._is_playing(selected.id):
                if self.state.meta.repress_mode == RepressMode.STOP:
                    self._stop_sound(selected.id)
                elif self.state.meta.repress_mode == RepressMode.OVERDUB:
                    self._play_sound(selected)
                elif self.state.meta.repress_mode == RepressMode.RESTART:
                    self._stop_sound(selected.id)
                    self._play_sound(selected)
            else:
                self._play_sound(selected)
        elif isinstance(selected, Category):
            self.db.category_adapter.update(selected, is_expanded=not selected.is_expanded)

    def _on_progress(self, progress: "PlayerProgress"):
        if self.progresses.append(progress):
            self.state.play_progress = self.progresses.total
            pos = self.sounds.get_sound_pos_if_visible(progress.sound.id, self.max_y)
            if pos is not None:
                selected = self.selected_object
                self._render_progress(pos, progress.progress, progress.sound, selected == progress.sound)
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
            self.state.play_progress = self.progresses.total
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
            self.db.sound_adapter.update(player.sound, play_count=player.sound.play_count + 1)

    def _play_sound(self, sound: "Sound"):
        player = WavPlayer(sound=sound, p=self.pyaudio, on_stop=self._on_stop, on_progress=self._on_progress)
        self.currently_playing.append(player)
        self.executor.submit(player.play)

    def _render_progress(self, pos: int, progress: float, sound: Sound, selected: bool):
        filled_attr = (
            sound.colors.value.regular.inverse.color_pair() if selected
            else sound.colors.value.selected.inverse.color_pair()
        )
        filled = "█" * round(progress * 20)
        self.window.addstr(pos, 30, filled, filled_attr)
        if len(filled) < 20:
            filler = "░" * (20 - len(filled))
            self.window.addstr(pos, 30 + len(filled), filler, sound.colors.value.selected.inverse.color_pair())

    def _render_object_at_pos(self, pos: int, obj: "Sound | Category | None", selected: bool):
        if obj:
            attr = (
                obj.colors.value.selected.color_pair() if selected
                else obj.colors.value.regular.color_pair()
            )
            text = obj.name

            if isinstance(obj, Category):
                text = f"[ {obj.name} | {obj.sound_count} sounds | {format_milliseconds(obj.duration_ms)} ]"
                if obj.is_expanded:
                    attr |= curses.A_BOLD
                else:
                    attr |= curses.A_ITALIC
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
                    self._render_progress(pos, progress, obj, selected)
        else:
            self.clear_line(0, pos)

    def _render_scrollbar(self):
        max_y = self.max_y
        visible_fraction = max_y / len(self.sounds)
        bar_height = coerce_between(round(max_y * visible_fraction), 1, max_y)
        pre_bar = coerce_at_most(round((self.sounds.offset * max_y) / len(self.sounds)), max_y - bar_height)
        post_bar = max_y - pre_bar - bar_height
        x = self.width - 1

        for y in range(pre_bar):
            self.window.addstr(y, x, "░")
        for y in range(pre_bar, pre_bar + bar_height):
            self.window.addstr(y, x, "█")
        for y in range(pre_bar + bar_height, pre_bar + bar_height + post_bar):
            self.window.addstr(y, x, "░")

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

    def cleanup(self):
        self.stop_all()

    def contents(self):
        super().contents()
        selected = self.sounds.selected
        self.sounds.update_offset(self.max_y, selected.idx if selected else None)
        for pos in range(self.max_y):
            idx = pos + self.sounds.offset
            obj = self.sounds.get_object_at_idx(idx)
            self._render_object_at_pos(pos=pos, obj=obj, selected=selected and selected.obj == obj)
        self._render_scrollbar()

    def get_placement(self, parent):
        return PanelPlacement(x=0, y=2, width=parent.width + 1, height=parent.height - 4, parent=parent)

    def on_state_change(self, name: str, value: Any):
        if name == "selected_sounds":
            self.redraw(force=True)
        elif name == "categories_with_sounds":
            diff = self.sounds.visible_diff(value, self.max_y)
            self.sounds = self.sounds.copy(
                categories_with_sounds=value,
                on_selected_change=self._on_selected_change,
            )
            selected = self.selected_object
            for (pos, obj) in diff:
                self._render_object_at_pos(pos, obj, selected == obj)
            self._render_scrollbar()
            self.redraw()

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
        selected = self.selected_object

        if key.meta:
            if key.s == "s":
                self.stop_all()
                return True
            return False

        if key.ctrl and key.c == 0 and not self.state.selected_sounds and isinstance(selected, Sound):
            # ctrl+space activates sound selection
            self.state.selected_sounds = self.state.selected_sounds.union({self.selected_object})
            self._step_single(1)
            return True

        if self.state.selected_sounds and isinstance(selected, Sound):
            if key.c in (curses.ascii.SP, curses.ascii.NL) or (key.ctrl and key.c == 0):
                if selected in self.state.selected_sounds:
                    self.state.selected_sounds = self.state.selected_sounds.difference({selected})
                else:
                    self.state.selected_sounds = self.state.selected_sounds.union({selected})
                self._step_single(1)
                return True

        if self.state.selected_sounds and key.c == curses.ascii.ESC:
            self.state.selected_sounds = set()
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
            elif key.c == curses.ascii.NL:
                self._on_enter_press()
            return True

        return False
