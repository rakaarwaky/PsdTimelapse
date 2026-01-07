"""
EXR Renderer Adapter
====================

High-performance EXR writer using OpenCV.
Writes Image (Beauty) and Velocity passes to separate files.
"""

import os

import cv2
import numpy as np
from PIL import Image


class ExrRendererAdapter:
    """
    Adapter for writing OpenEXR files.
    """

    def __init__(self):
        # Enable EXR support in OpenCV env
        os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
        self.compression_flags = [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_FLOAT]

        # Future: Add compression tuning if needed
        # cv2.IMWRITE_EXR_COMPRESSION can be set if OpenCV version supports it

    def save_frame(
        self,
        beauty_image: Image.Image,
        velocity_map: Image.Image,
        output_path: str,
        frame_number: int,
    ) -> list[str]:
        """
        Save beauty and velocity passes as EXR files.

        Args:
            beauty_image: RGBA PIL Image
            velocity_map: RGB PIL Image (R=VelX, G=VelY, B=0)
            output_path: Base directory or file path template
            frame_number: Current frame index

        Returns:
            List of saved file paths.
        """
        saved_files = []

        # Ensure directory exists
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        # Construct Paths
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        # Handle "frame_001" pattern if provided, else append number
        if "%d" in base_name or "{}" in base_name:
            # Assume user handled formatting in path, not supported properly here without string format
            # Simpler: Just append suffix
            pass

        # Standardize Naming:
        # Beauty:   path/filename_0001.exr
        # Velocity: path/filename_0001_vector.exr

        beauty_filename = f"{base_name}_{frame_number:04d}.exr"
        velocity_filename = f"{base_name}_{frame_number:04d}_vector.exr"

        beauty_full_path = os.path.join(out_dir, beauty_filename)
        velocity_full_path = os.path.join(out_dir, velocity_filename)

        # 1. Write Beauty (RGBA)
        # Convert PIL (RGBA) -> NumPy (BGRA for OpenCV)
        beauty_np = np.array(beauty_image).astype(np.float32) / 255.0
        if beauty_np.shape[2] == 4:
            beauty_bgra = cv2.cvtColor(beauty_np, cv2.COLOR_RGBA2BGRA)
        else:
            beauty_bgra = cv2.cvtColor(beauty_np, cv2.COLOR_RGB2BGR)

        cv2.imwrite(beauty_full_path, beauty_bgra, self.compression_flags)
        saved_files.append(beauty_full_path)

        # 2. Write Velocity (RGB)
        # Expecting velocity_map to be RGB PIL Image where:
        # R = Map X (-max to +max mapped to 0-1 or raw float?)
        # Wait, PIL Image is usually uint8. Velocity needs Float Precision.
        # IF velocity_map is passed as PIL Image, it might be truncated!
        # better to accept numpy array for velocity or raw data.

        # UPDATE: We should accept Raw Float Data for velocity to preserve precision.
        # But if interface is PIL Image, we assume it's already encoded?
        # NO, VelocityCompositor should produce Float Data.

        # Handling Float input if velocity_m is numpy array
        if isinstance(velocity_map, np.ndarray):
            vel_data = velocity_map
        else:
            # Fallback (Low Precision)
            vel_data = np.array(velocity_map).astype(np.float32)

        # OpenCV expects BGR
        # Input Velocity: R=X, G=Y, B=0
        # Output EXR: B=0, G=Y, R=X (swapped)
        vel_bgr = np.zeros_like(vel_data)
        vel_bgr[:, :, 0] = vel_data[:, :, 2]  # B -> B
        vel_bgr[:, :, 1] = vel_data[:, :, 1]  # G -> G
        vel_bgr[:, :, 2] = vel_data[:, :, 0]  # R -> R

        cv2.imwrite(velocity_full_path, vel_bgr, self.compression_flags)
        saved_files.append(velocity_full_path)

        return saved_files
