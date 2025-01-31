from dataclasses import dataclass
from typing import Self

from soundboard_fuck.db.sqlite.comparison import Comparison, Equals


@dataclass
class Expression:
    key: "Expression | str"
    value: "Comparison | str"

    def __post_init__(self):
        if isinstance(self.key, str):
            parts = self.key.split("__")
            if len(parts) > 1 and parts[-1] == "lower":
                self.key = Lower(key="__".join(parts[:-1]), value=self.value)

    def __str__(self):
        value = Equals(self.value) if not isinstance(self.value, Comparison) else self.value
        return str(self.key) + str(value)

    @property
    def key_string(self):
        if isinstance(self.key, str):
            return self.key
        return self.key.key_string

    def add_prefix(self, prefix: str) -> Self:
        if isinstance(self.key, Expression):
            self.key = self.key.add_prefix(prefix)
        else:
            self.key = f"{prefix}.`{self.key}`"
        return self


@dataclass
class Lower(Expression):
    def __str__(self):
        return f"LOWER({self.key})"
