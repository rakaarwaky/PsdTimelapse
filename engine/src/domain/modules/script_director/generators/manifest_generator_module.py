"""
ManifestGeneratorModule: Generate JSON manifest for compositor consumption.
Dependencies: Timeline, LayerEntity (BLIND MODULE - no peer imports)

BLIND LOGIC: This module is "Staff" level. It does NOT import from peer
submodules (planners/). All external dependencies are injected or imported
"""

from __future__ import annotations

import os
from typing import Any

from ....entities.timeline_entity import TimelineEntity
from ....value_objects.manifest.compositor_manifest_value import CompositorManifest
from ....value_objects.manifest.layer_manifest_value import LayerManifest


def generate_manifest(
    timeline: TimelineEntity, fps: int = 24, layer_names: dict[str, Any] | None = None
) -> CompositorManifest:
    """
    Generate compositor manifest from timeline.

    Args:
        timeline: Animation timeline with actions.
        fps: Frames per second.
        layer_names: Optional dict mapping layer_id -> layer_name.

    Returns:
        CompositorManifest object.
    """
    total_duration = timeline.total_duration
    total_frames = int(total_duration * fps)

    # Group actions by layer
    layer_actions: dict[str, Any] = {}
    for action in timeline.actions:
        if action.layer_id not in layer_actions:
            layer_actions[action.layer_id] = []
        layer_actions[action.layer_id].append(action)

    layers = []
    for layer_id, actions in layer_actions.items():
        if not actions:
            continue

        # Calculate visible range from actions
        min_start = min(a.start_time for a in actions)
        max_end = max(a.start_time + a.duration for a in actions)

        start_frame = int(min_start * fps)
        end_frame = int(max_end * fps)

        # Get animation type from first action
        anim_type = actions[0].action_type.value.lower() if actions else "drag"

        # Create folder name from layer_id (sanitize)
        folder_name = layer_id.replace(" ", "_").replace("/", "_").lower()

        layer_name = layer_names.get(layer_id, layer_id) if layer_names else layer_id

        layers.append(
            LayerManifest(
                id=layer_id,
                name=layer_name,
                sequence_folder=f"{folder_name}/",
                animation_type=anim_type,
                visible_range=(start_frame, end_frame),
            )
        )

    return CompositorManifest(
        total_frames=total_frames, fps=fps, duration_seconds=total_duration, layers=layers
    )


def save_manifest(manifest: CompositorManifest, output_path: str) -> str:
    """
    Save manifest to JSON file.

    Args:
        manifest: CompositorManifest to save.
        output_path: Directory or full file path.

    Returns:
        Full path to saved manifest file.
    """
    if os.path.isdir(output_path):
        file_path = os.path.join(output_path, "manifest.json")
    else:
        file_path = output_path

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as f:
        f.write(manifest.to_json())

    return file_path


def generate_and_save_manifest(
    timeline: TimelineEntity,
    output_path: str,
    fps: int = 24,
    layer_names: dict[str, Any] | None = None,
) -> tuple[CompositorManifest, str]:
    """
    Generate and save manifest in one call.

    Returns:
        Tuple of (manifest, file_path).
    """
    manifest = generate_manifest(timeline, fps, layer_names)
    file_path = save_manifest(manifest, output_path)
    return manifest, file_path
