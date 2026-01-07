"""
UIHelper: Utilities for UI rendering preparation.
Migrated from render_manager to pipeline_manager.
"""

from typing import Any

from ....entities.world_entity import WorldEntity


def build_ui_layer_list(world: WorldEntity) -> list[dict[str, Any]]:
    """
    Build layer info list for UI panel display.

    Args:
        world: The loaded WorldEntity

    Returns:
        List of dicts containing layer metadata for UI
    """
    if not world:
        return []

    layers = []
    # Iterate visible layers
    # Note: scene.iterate_visible() yields LayerEntity
    for layer in world.scene.iterate_visible():
        layers.append(
            {
                "name": layer.name,
                "visible": layer.visible,
                "locked": layer.name.lower() == "background",  # Background = locked
            }
        )
    return layers
