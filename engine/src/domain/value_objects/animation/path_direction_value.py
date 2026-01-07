from enum import Enum


class PathDirection(Enum):
    """Animation path direction."""

    HORIZONTAL = "horizontal"  # Left-to-right or right-to-left
    VERTICAL = "vertical"  # Top-to-bottom or bottom-to-top
