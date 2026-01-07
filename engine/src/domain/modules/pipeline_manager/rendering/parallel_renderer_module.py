from __future__ import annotations

from typing import Any
from collections.abc import Callable
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
    from PIL import Image
    import io
    from PIL import Image
        import io


"""
ParallelRenderer: Multiprocessing frame rendering for Phase 4 optimization.
Uses Python's multiprocessing to render frames in parallel across CPU cores.
Migrated from render_manager to pipeline_manager.
"""



try:

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


@dataclass
class FrameTask:
    """A single frame rendering task."""

    frame_num: int
    timestamp: float
    layer_states: dict[str, Any]  # Serializable layer states


@dataclass
class FrameResult:
    """Result of rendering a single frame."""

    frame_num: int
    image_bytes: bytes  # PNG bytes for serialization
    width: int
    height: int


def _render_frame_worker(args: tuple[Any, ...]) -> tuple[int, bytes, int, int]:
    """
    Worker function for rendering a single frame.

    This runs in a separate process, so all data must be serializable.

    Args:
        args: Tuple of (frame_num, timestamp, layer_states_dict,
                       world_width, world_height, layer_images_dict)

    Returns:
        Tuple of (frame_num, png_bytes, width, height)
    """


    (frame_num, timestamp, layer_states, world_width, world_height, layer_images_bytes) = args

    # Create blank PSD canvas
    psd = Image.new("RGBA", (world_width, world_height), (255, 255, 255, 255))

    # Decode layer images from bytes
    layer_images = {}
    for layer_id, img_bytes in layer_images_bytes.items():
        if img_bytes:
            layer_images[layer_id] = Image.open(io.BytesIO(img_bytes))

    # Composite layers
    for layer_id, state in layer_states.items():
        if not state.get("visible", True) or state.get("opacity", 1.0) <= 0:
            continue

        if layer_id not in layer_images:
            continue

        layer_img = layer_images[layer_id]

        # Apply opacity if needed
        opacity = state.get("opacity", 1.0)
        if opacity < 1.0:
            if layer_img.mode != "RGBA":
                layer_img = layer_img.convert("RGBA")
            r, g, b, a = layer_img.split()
            a = a.point(lambda x, op=opacity: int(x * op))
            layer_img = Image.merge("RGBA", (r, g, b, a))

        # Get position from state
        pos_x = int(state.get("bounds_x", 0))
        pos_y = int(state.get("bounds_y", 0))

        # Paste layer
        try:
            if layer_img.mode == "RGBA":
                psd.paste(layer_img, (pos_x, pos_y), layer_img)
            else:
                psd.paste(layer_img, (pos_x, pos_y))
        except Exception:
            pass

    # Encode result as PNG bytes
    buffer = io.BytesIO()
    psd.save(buffer, format="PNG")
    png_bytes = buffer.getvalue()

    return (frame_num, png_bytes, world_width, world_height)


class ParallelRenderer:
    """
    Renders frames in parallel using multiprocessing.

    Significant speedup on multi-core CPUs (Ryzen 5 5600 = 6 cores).
    """

    def __init__(self, workers: int | None = None):
        """
        Initialize parallel renderer.

        Args:
            workers: Number of worker processes. Defaults to cpu_count() - 1.
        """
        if not HAS_PILLOW:
            raise ImportError("Pillow required")

        self._workers = workers or max(1, cpu_count() - 1)

    def render_frames(
        self,
        world_width: int,
        world_height: int,
        layer_images: dict[str, Any],  # layer_id -> PIL.Image
        frame_tasks: list[FrameTask],
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[Image.Image]:
        """
        Render multiple frames in parallel.

        Args:
            world_width: PSD width
            world_height: PSD height
            layer_images: Dict mapping layer_id to PIL.Image
            frame_tasks: List of FrameTask objects
            progress_callback: Optional callback(current, total)

        Returns:
            List of PIL.Image frames in order
        """

        # Serialize layer images to bytes for passing to workers
        layer_images_bytes: dict[str, bytes | None] = {}
        for layer_id, img in layer_images.items():
            if img is not None:
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                layer_images_bytes[layer_id] = buffer.getvalue()
            else:
                layer_images_bytes[layer_id] = None

        # Prepare tasks as serializable tuples
        tasks = []
        for task in frame_tasks:
            # Convert LayerAnimState to dict for serialization
            layer_states_dict = {}
            for layer_id, state in task.layer_states.items():
                layer_states_dict[layer_id] = {
                    "visible": getattr(state, "visible", True),
                    "opacity": getattr(state, "opacity", 1.0),
                    "bounds_x": getattr(state, "bounds_x", 0),
                    "bounds_y": getattr(state, "bounds_y", 0),
                }

            tasks.append(
                (
                    task.frame_num,
                    task.timestamp,
                    layer_states_dict,
                    world_width,
                    world_height,
                    layer_images_bytes,
                )
            )

        # Render in parallel
        results = []
        total = len(tasks)

        with Pool(self._workers) as pool:
            for i, result in enumerate(pool.imap(_render_frame_worker, tasks)):
                results.append(result)
                if progress_callback and (i + 1) % 10 == 0:
                    progress_callback(i + 1, total)

        # Sort by frame number and decode images
        results.sort(key=lambda x: x[0])

        frames = []
        for _frame_num, png_bytes, _w, _h in results:
            img = Image.open(io.BytesIO(png_bytes))
            frames.append(img)

        return frames

    @property
    def worker_count(self) -> int:
        """Get number of worker processes."""
        return self._workers