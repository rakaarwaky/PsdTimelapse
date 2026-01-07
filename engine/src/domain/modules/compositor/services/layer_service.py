from PIL import Image

from ....entities.layer_entity import LayerEntity


class LayerRetrievalService:
    """
    Manages layer image retrieval and caching.
    Target Size: < 20 lines.
    """

    def __init__(self) -> None:
        self._layer_cache: dict[str, Image.Image] = {}
        # Scaled cache logic omitted for simplicity/YAGNI

    def get_layer_image(self, layer: LayerEntity) -> Image.Image | None:
        if layer.id in self._layer_cache:
            return self._layer_cache[layer.id]

        if isinstance(layer.image_data, Image.Image):
            self._layer_cache[layer.id] = layer.image_data
            return layer.image_data

        return None

    def clear_cache(self) -> None:
        self._layer_cache.clear()
