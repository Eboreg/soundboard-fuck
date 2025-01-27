from dataclasses import dataclass
from uuid import UUID


@dataclass
class PlayerProgress:
    player_id: UUID
    sound_id: int
    created: float
    progress: float
