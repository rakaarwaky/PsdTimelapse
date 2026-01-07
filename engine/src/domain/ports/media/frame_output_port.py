from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    FrameData = Any
else:
    FrameData = Any


class FrameOutputPort(ABC):
    """
    Abstract port for frame output.  # noqa: PLR0913, PLR0912
    Adapters implement this for EXR, MP4, etc.
    """

    @abstractmethod
    def write_frame(self, frame_data: FrameData, output_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def finalize(self) -> str:
        raise NotImplementedError
