import string
from typing import TypeVar


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
