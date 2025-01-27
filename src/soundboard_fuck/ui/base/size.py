from dataclasses import dataclass


@dataclass
class Size:
    width: int
    height: int

    @classmethod
    def from_curses(cls, yx: tuple[int, int]):
        return cls(width=yx[1], height=yx[0])
