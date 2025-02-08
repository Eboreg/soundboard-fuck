import re
import string
from pathlib import Path
from typing import Any, Mapping, Sized, TypeVar, cast

from soundboard_fuck.constants import SOUND_EXTENSIONS
from platformdirs import user_config_dir


_Number = TypeVar("_Number", int, float)
_T = TypeVar("_T")

KILOBYTE = pow(2, 10)
MEGABYTE = pow(2, 20)
GIGABYTE = pow(2, 30)
TERABYTE = pow(2, 40)


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


def pad_with_nulls(lst: list[_T], length: int) -> list[_T | None]:
    ret = cast(list[_T | None], lst)

    if len(ret) < length:
        for _ in range(len(ret), length):
            ret.append(None)

    return ret


def format_filesize(size: int):
    if size < KILOBYTE:
        return str(size)
    if size < MEGABYTE:
        return f"{(size / KILOBYTE):.2f}K"
    if size < GIGABYTE:
        return f"{(size / MEGABYTE):.2f}M"
    if size < TERABYTE:
        return f"{(size / GIGABYTE):.2f}G"
    return f"{(size / TERABYTE):.2f}T"


def step_list(lst: Sized, current_idx: int, steps: int, wrap: bool = True) -> int:
    if not wrap:
        if current_idx + steps < 0:
            return 0
        if current_idx + steps >= len(lst):
            return len(lst) - 1

    if abs(steps) > len(lst):
        steps = steps % len(lst) if steps >= 0 else steps % (len(lst) * -1)
    if current_idx + steps >= len(lst):
        return steps - (len(lst) - current_idx)
    if current_idx + steps < 0:
        return len(lst) + steps
    return current_idx + steps


def step_dict(dct: Mapping[_T, Any], current_key: _T, steps: int, wrap: bool = True) -> _T:
    keys = list(dct.keys())
    current_idx = keys.index(current_key)
    new_idx = step_list(keys, current_idx, steps, wrap)
    return keys[new_idx]


def list_directory_sounds(directory: Path, recursive: bool) -> list[Path]:
    path_generator = directory.glob("*") if not recursive else directory.rglob("*")
    return [p.absolute() for p in path_generator if p.is_file() and p.suffix.lower().strip(".") in SOUND_EXTENSIONS]


def iterate_directory_sounds(directory: Path, recursive: bool):
    path_generator = directory.glob("*") if not recursive else directory.rglob("*")
    for path in path_generator:
        if path.is_file() and path.suffix.lower().strip(".") in SOUND_EXTENSIONS:
            yield path.absolute()
