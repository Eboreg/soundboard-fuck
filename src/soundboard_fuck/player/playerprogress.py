import time
from dataclasses import dataclass
from uuid import UUID

from soundboard_fuck.data.sound import Sound


@dataclass
class PlayerProgress:
    player_id: UUID
    sound: Sound
    created: int
    progress: float

    @property
    def remaining_ms(self):
        return int(self.sound.duration_ms * (1.0 - self.progress))

    @property
    def ends(self):
        return int((time.time() * 1000) + self.remaining_ms)
