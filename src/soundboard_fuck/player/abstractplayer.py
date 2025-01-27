from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable
from uuid import UUID

from soundboard_fuck.player.playerprogress import PlayerProgress
from soundboard_fuck.utils import coerce_between


if TYPE_CHECKING:
    from soundboard_fuck.data.sound import Sound


class AbstractPlayer(ABC):
    sound: "Sound"
    is_playing: bool
    id: UUID
    created: float
    on_progress: Callable[[PlayerProgress], Any]
    progress: float

    @abstractmethod
    def play(self):
        ...

    @abstractmethod
    def stop(self):
        ...

    def _on_progress(self, progress: float):
        self.progress = coerce_between(progress, 0.0, 1.0)
        self.on_progress(
            PlayerProgress(
                player_id=self.id,
                sound_id=self.sound.id,
                created=self.created,
                progress=self.progress,
            )
        )
