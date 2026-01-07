"""
Encoder: Video encoding adapters.

Exports:
    - MoviePyEncoderAdapter: CPU-based video encoder (MoviePy)
    - NvencEncoderAdapter: GPU-accelerated encoder (NVIDIA NVENC)
"""

from .moviepy_encoder_adapter import MoviePyAdapter
from .nvenc_encoder_adapter import NvencEncoderAdapter

# Alias following brand convention
MoviePyEncoderAdapter = MoviePyAdapter

__all__ = [
    "MoviePyEncoderAdapter",
    "MoviePyAdapter",
    "NvencEncoderAdapter",
]
