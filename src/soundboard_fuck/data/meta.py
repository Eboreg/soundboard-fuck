from dataclasses import dataclass
from soundboard_fuck.data.model import Model
from soundboard_fuck.enums import RepressMode


@dataclass
class Meta(Model):
    db_version: int
    repress_mode: RepressMode = RepressMode.STOP
    convert_to_wav: bool = False
    default_category: int | None = None
    id: int | None = None
