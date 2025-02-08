import time
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from soundboard_fuck.player.abstractplayer import AbstractPlayer
    from soundboard_fuck.player.playerprogress import PlayerProgress


class ProgressCollection:
    _progresses: "dict[int, PlayerProgress]"

    def __init__(self):
        self._progresses = {}

    def __contains__(self, item):
        return item in self._progresses

    @property
    def total(self) -> float | None:
        first = min(self._progresses.values(), key=lambda p: p.created, default=None)
        last = max(self._progresses.values(), key=lambda p: p.ends, default=None)

        if first and last:
            now = int(time.time() * 1000)
            total = last.ends - first.created
            elapsed = now - first.created
            return elapsed / total

        return None

    def append(self, progress: "PlayerProgress") -> bool:
        if (
            not progress.sound.id in self or
            self._progresses[progress.sound.id].created <= progress.created
        ):
            self._progresses[progress.sound.id] = progress
            return True
        return False

    def get_sound_progress(self, sound_id: int) -> float | None:
        if sound_id in self:
            return self._progresses[sound_id].progress
        return None

    def items(self):
        return [(k, v.progress) for k, v in self._progresses.items()]

    def delete(self, player: "AbstractPlayer") -> bool:
        if player.sound.id in self and self._progresses[player.sound.id].player_id == player.id:
            del self._progresses[player.sound.id]
            return True
        return False
