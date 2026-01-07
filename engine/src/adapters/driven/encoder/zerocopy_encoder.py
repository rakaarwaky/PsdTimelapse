"""
Zero-copy GPU encoder using PyNvVideoCodec.
Wraps the encoder interactions to allow direct GPU buffer feeding.
"""

from __future__ import annotations

from typing import Any

try:
    import PyNvVideoCodec as nvc

    HAS_NVCODEC = True
except ImportError:
    HAS_NVCODEC = False


class ZeroCopyEncoder:
    """
    Zero-copy GPU video encoder using NVIDIA Video Codec SDK.
    """

    def __init__(
        self,
        width: int,
        height: int,
        fps: int = 30,
        codec: str = "h264",
        bitrate: int = 8_000_000,
        gpu_id: int = 0,
    ):
        if not HAS_NVCODEC:
            raise ImportError("PyNvVideoCodec not installed")

        self.width = width
        self.height = height
        self.fps = fps
        self._gpu_id = gpu_id

        options = {
            "gpu_id": str(gpu_id),
            "codec": "h264" if codec.lower() == "h264" else "hevc",
            "preset": "P4",
            "tuning_info": "high_quality",
            "profile": "high" if codec.lower() == "h264" else "main",
            "rc_mode": "VBR",
            "avg_bitrate": str(bitrate),
            "max_bitrate": str(bitrate * 2),
            "gop_length": str(fps * 2),
            "framerate": str(fps),
        }

        # Encoder configuration
        # Assuming we now feed valid CUDA array interface objects (CuPy arrays)
        # We use "NV12" format because our Converter produces NV12.
        self._encoder = nvc.CreateEncoder(
            width,
            height,
            "NV12",
            False,  # use_cpu_input=False
            **options,
        )

        print(f"✓ ZeroCopyEncoder configured: {width}x{height} @ {fps}fps")

    def encode_frame(self, frame_obj: Any) -> bytes:
        """
        Encode a single frame.
        Input can be any object supporting __cuda_array_interface__ (like CuPy array),
        or numpy array.
        """
        # PyNvVideoCodec 'Encode' expects different things depending on setup.
        # If use_cpu_input=False, it might expect a raw device pointer (int).
        # CuPy arrays expose .data.ptr which is the raw address.
        input_data = frame_obj
        if hasattr(frame_obj, "data") and hasattr(frame_obj.data, "ptr"):
            input_data = frame_obj.data.ptr

        try:
            packet = self._encoder.Encode(input_data)
            if packet:
                return bytes(packet)
        except Exception as e:
            # Fallback debug or re-raise
            # print(f"Encode failed with input type {type(input_data)}: {e}")
            raise e
        return b""

    def close(self) -> None:
        pass
