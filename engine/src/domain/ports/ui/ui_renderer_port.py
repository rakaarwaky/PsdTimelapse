from abc import ABC, abstractmethod
from typing import Any

from PIL import Image


class UIRendererPort(ABC):
    """
    Abstract port for UI rendering.
    Adapter: UIRendererCore
    """

    @abstractmethod
    def render_static_ui(self, layers: list[dict[str, Any]] = None) -> Image.Image:
        raise NotImplementedError
