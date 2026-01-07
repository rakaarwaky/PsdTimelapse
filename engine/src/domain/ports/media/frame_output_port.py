from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....animator.generators.layer_state_generator_module import FrameData


class FrameOutputPort(ABC):
    """
    Abstract port for frame output.
    Adapters implement this for EXR, MP4, etc.
    """

    @abstractmethod
    def write_frame(self, frame_data: "FrameData", output_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def finalize(self) -> str:
        raise NotImplementedError
