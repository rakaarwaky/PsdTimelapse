"""
SceneEntity: Tree structure for layer hierarchy.
Dependencies: LayerEntity
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field

from .layer_entity import LayerEntity


@dataclass
class SceneEntity:
    """Scene graph containing the layer hierarchy (tree structure)."""

    root_layers: list[LayerEntity] = field(default_factory=list)
    _layer_map: dict[str, LayerEntity] = field(default_factory=dict, repr=False)
    _children_map: dict[str, list[LayerEntity]] = field(default_factory=dict, repr=False)

    def add_layer(self, layer: LayerEntity) -> None:
        """Add a layer to the scene."""
        self._layer_map[layer.id] = layer

        if layer.parent_id is None:
            self.root_layers.append(layer)
        else:
            if layer.parent_id not in self._children_map:
                self._children_map[layer.parent_id] = []
            self._children_map[layer.parent_id].append(layer)

    def find_layer(self, layer_id: str) -> LayerEntity | None:
        """Find a layer by its ID."""
        return self._layer_map.get(layer_id)

    def find_by_name(self, name: str) -> LayerEntity | None:
        """Find first layer matching the given name."""
        for layer in self._layer_map.values():
            if layer.name == name or layer.clean_name == name:
                return layer
        return None

    def get_children(self, parent_id: str) -> list[LayerEntity]:
        """Get direct children of a layer."""
        return self._children_map.get(parent_id, [])

    def iterate_all(self) -> Iterator[LayerEntity]:
        """Iterate all layers in depth-first order."""

        def traverse(layers: list[LayerEntity]) -> Iterator[LayerEntity]:
            for layer in layers:
                yield layer
                if layer.is_group:
                    yield from traverse(self.get_children(layer.id))

        yield from traverse(self.root_layers)

    def iterate_visible(self) -> Iterator[LayerEntity]:
        """Iterate only visible layers (respecting parent visibility)."""

        def traverse(layers: list[LayerEntity], parent_visible: bool) -> Iterator[LayerEntity]:
            for layer in layers:
                is_visible = parent_visible and layer.visible
                if is_visible and not layer.is_group:
                    yield layer
                if layer.is_group:
                    yield from traverse(self.get_children(layer.id), is_visible)

        yield from traverse(self.root_layers, True)

    def filter_layers(self, predicate: Callable[[LayerEntity], bool]) -> list[LayerEntity]:
        """Filter layers using a predicate function."""
        return [layer for layer in self.iterate_all() if predicate(layer)]

    @property
    def layer_count(self) -> int:
        """Total number of layers in scene."""
        return len(self._layer_map)

    @property
    def visible_count(self) -> int:
        """Number of visible layers (non-group)."""
        return sum(1 for _ in self.iterate_visible())

    def __repr__(self) -> str:
        return f"Scene({self.layer_count} layers, {self.visible_count} visible)"
