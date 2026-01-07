from dataclasses import dataclass
from typing import Any


@dataclass
class CursorStyle:
    size: int = 24
    color: tuple[Any, ...] = (30, 30, 30, 220)
    outline_color: tuple[Any, ...] = (255, 255, 255, 180)
    outline_width: int = 2
