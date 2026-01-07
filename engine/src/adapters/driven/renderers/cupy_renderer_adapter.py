from typing import Any

import cupy as cp  # type: ignore[import-not-found]
import numpy as np

from domain.ports.render.gpu_renderer_port import GpuRendererPort  # type: ignore[import-not-found]

from .cupy_color_converter import CupyColorConverter
from .cupy_compositor import CupyCompositor


class CupyRendererAdapter(GpuRendererPort):  # type: ignore[misc]
    """
    Adapter for GPU Rendering using CuPy and NVENC.
    Implements GpuRendererPort.
    """

    def __init__(self) -> None:
        print("Initializing CupyRendererAdapter...")
        # Lazy init resources on first render to avoid overhead if unused
        self.compositor = None
        self.converter = None
        self.encoder = None
        self.nv12_buffer = None
        self.canvas = None
        self.width = 0
        self.height = 0

    def _init_resources(self, width: int, height: int, fps: int) -> None:
        if self.compositor and self.width == width and self.height == height:  # type: ignore[unreachable]
            return  # type: ignore[unreachable]

        self.width = width
        self.height = height

        # 1. Compositor (Alpha Blend Kernel)
        self.compositor = CupyCompositor()  # type: ignore[assignment]

        # 2. Converter (RGBA->NV12 Kernel)
        self.converter = CupyColorConverter()  # type: ignore[assignment]

        # 3. Canvas & Buffers
        self.canvas = cp.zeros((height, width, 4), dtype=cp.float32)

        # Pre-allocate NV12 Buffer
        nv12_size = int(width * height * 1.5)
        self.nv12_buffer = cp.zeros(nv12_size, dtype=cp.uint8)

    def render(  # type: ignore[no-untyped-def]
        self,
        composited_frames: list[Any],  # Pre-composited PIL frames from Domain
        config,  # RenderConfig
        progress_callback=None,
    ) -> str:
        """
        Encode pre-composited frames to video using GPU (NVENC).

        GPU adapter only does encoding - all compositing is done in Domain.
        """
        # 0. Lazy Init
        self._init_resources(config.width, config.height, config.fps)

        # 1. Initialize Encoder
        from adapters.driven.encoder.ffmpeg_pipe_encoder import (  # type: ignore[import-not-found]
            FfmpegPipeEncoder,
        )

        # type: ignore[unused-ignore]
        self.encoder = FfmpegPipeEncoder(
            config.width, config.height, config.fps, output_path=config.output_path
        )

        # Calculate total frames from config (composited_frames may be a generator)
        total_frames = int(config.duration * config.fps) if hasattr(config, "duration") else 0
        print("Starting GPU Encode (streaming mode)")

        # 2. Encode each pre-composited frame
        for i, frame in enumerate(composited_frames):
            if isinstance(frame, cp.ndarray):
                # ZERO COPY PATH: Frame is already on GPU (from GpuPipelineManager)
                # Frame is float32 [0.0, 1.0] RGBA (H, W, 4)
                self.canvas[:] = frame
            else:
                # CPU FALLBACK PATH: Convert PIL to buffer and upload  # type: ignore[index]
                # Convert PIL to numpy array
                frame_np = np.array(frame.convert("RGB")).astype(np.float32) / 255.0

                # Upload to GPU
                frame_gpu = self._upload_to_pinned_memory(
                    np.concatenate(
                        [frame_np, np.ones((*frame_np.shape[:2], 1), dtype=np.float32)], axis=2
                    )
                )

                # Copy to canvas
                self.canvas[:] = frame_gpu

            # Convert colorspace  # type: ignore[index]
            canvas_ptr = self.canvas.data.ptr
            self.converter.convert(
                canvas_ptr,
                self.width,
                self.height,
                output_buffer=self.nv12_buffer,  # type: ignore[union-attr]
            )  # type: ignore[union-attr]

            # Encode
            self.encoder.encode_frame(self.nv12_buffer)

            if progress_callback and i % 30 == 0:  # type: ignore[union-attr]
                progress_callback(i, total_frames)

        self.encoder.release()
        return config.output_path

    # type: ignore[union-attr]
    def _upload_to_pinned_memory(self, numpy_img: np.ndarray) -> cp.ndarray:  # type: ignore[no-any-return]
        """Helper to move numpy image to GPU via Pinned Memory."""
        h, w, c = numpy_img.shape
        size_bytes = w * h * c * 4  # Float32
        mem = cp.cuda.alloc_pinned_memory(size_bytes)
        pinned_view = np.ndarray((h, w, c), dtype=np.float32, buffer=mem)

        if numpy_img.dtype == np.uint8:
            pinned_view[:] = numpy_img.astype(np.float32) / 255.0
        else:
            pinned_view[:] = numpy_img.astype(np.float32)

        return cp.asarray(pinned_view)

    def _render_batch(
        self,
        static_bg_gpu: cp.ndarray,  # type: ignore[no-untyped-def]
        dynamic_assets_gpu: dict[str, Any],
        timeline_actions: list[Any],
        total_frames: int,
        progress_callback=None,
    ) -> None:
        """Execute the render loop entirely on GPU."""
        print(f"Starting GPU Batch Render: {total_frames} frames")

        canvas_ptr = self.canvas.data.ptr

        for i, frame_config in enumerate(timeline_actions):  # type: ignore[union-attr]
            # 1. Reset Canvas
            self.canvas[:] = static_bg_gpu

            # 2. Composite  # type: ignore[index]
            for asset_key, x, y, _opacity in frame_config:
                if asset_key in dynamic_assets_gpu:
                    asset = dynamic_assets_gpu[asset_key]
                    # TODO: Apply opacity in compositor.blend if needed
                    self.compositor.blend(self.canvas, asset, int(x), int(y))

            # 3. Convert  # type: ignore[union-attr]
            self.converter.convert(
                canvas_ptr, self.width, self.height, output_buffer=self.nv12_buffer
            )  # type: ignore[union-attr]

            # 4. Encode
            self.encoder.encode_frame(self.nv12_buffer)

            if progress_callback and i % 30 == 0:  # type: ignore[union-attr]
                progress_callback(i, total_frames)

        self.encoder.release()
