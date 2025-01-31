from pathlib import Path
import re
import string
from typing import TypeVar
from platformdirs import user_config_dir


_Number = TypeVar("_Number", int, float)


def coerce_between(value: _Number, min_value: _Number, max_value: _Number) -> _Number:
    if max_value < min_value:
        raise ValueError(f"max_value ({max_value}) is less than min_value ({min_value})")
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def coerce_at_least(value: _Number, min_value: _Number) -> _Number:
    if value < min_value:
        return min_value
    return value


def coerce_at_most(value: _Number, max_value: _Number) -> _Number:
    if value > max_value:
        return max_value
    return value


def char_diff(c1: str, c2: str) -> int:
    return abs(ord(c1) - ord(c2))


def str_to_floats(s: str) -> tuple[float, float]:
    base_value = 0.0
    add_extra = 0.0

    for idx, char in enumerate(s.upper()):
        factor = pow(len(string.ascii_uppercase), -1 * idx)
        if char in string.ascii_uppercase:
            base_value += string.ascii_uppercase.index(char) * factor
        else:
            add_extra += 100 * factor

    return base_value, base_value + add_extra


def str_floats_diff(f1: tuple[float, float], f2: tuple[float, float]) -> float:
    return min(
        abs(f1[0] - f2[0]),
        abs(f1[0] - f2[1]),
        abs(f1[1] - f2[0]),
        abs(f1[1] - f2[1]),
    )


def str_diff(s1: str, s2: str) -> float:
    return str_floats_diff(str_to_floats(s1), str_to_floats(s2))


def format_milliseconds(ms: float | int):
    seconds = ms / 1000 % 60
    minutes = int(ms / 1000 / 60 % 60)
    hours = int(ms / 1000 / 60 / 60)
    if hours > 0:
        return f"{hours}h{minutes:02d}m{seconds:02.0f}s"
    if minutes > 0:
        return f"{minutes:02d}m{seconds:02.0f}s"
    return f"{seconds:.2f}s"


def get_config_dir():
    path = Path(user_config_dir("soundboard-fuck"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_local_sounds_dir():
    path = get_config_dir() / "sounds"
    path.mkdir(exist_ok=True)
    return path


def split_to_rows(text: str, width: int):
    text = re.sub(r" {2,}", " ", text)
    hyphensplit: list[str] = [t for t in re.split(r"(.*?-)", text) if t]
    words = [tt for t in hyphensplit for tt in t.split(" ")]
    lines = []
    line = ""
    for word in words:
        if len(word) > width:
            lines.append(line)
            lines.append(word[:width])
            line = ""
            word = word[width:]
        if len(line) + len(word) + 1 > width:
            lines.append(line)
            line = ""
        if not line or line.endswith("-"):
            line += word
        else:
            line += " " + word
    if line:
        lines.append(line)
    return lines
