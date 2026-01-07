import numpy as np        # noqa: PLR0913, PLR0912
from PIL import Image, ImageDraw
from domain.entities import layer_entity as le
from domain.value_objects import Vector2, Rect

class MockGrid(le.LayerEntity):
    def __init__(self, uid, color, x, y, w, h, z, label=""):        # noqa: PLR0913, PLR0912
        super().__init__(
            id=uid,
            name=f"Layer_{uid}",
            z_index=z,
            position=Vector2(x, y),
            bounds=Rect(x, y, w, h),
            opacity=1.0,
            visible=True
        )
        self.color = color
        self.w = w
        self.h = h
        self.label = label

    def _create_mock_image(self):
        # Create blank RGBA image
        img = Image.new('RGBA', (self.w, self.h), self.color)
        d = ImageDraw.Draw(img)

        # Draw border
        d.rectangle([0, 0, self.w-1, self.h-1], outline=(0,0,0,255), width=2)

        # Draw cross lines
        d.line([0, 0, self.w, self.h], fill=(255,255,255,128), width=2)
        d.line([0, self.h, self.w, 0], fill=(255,255,255,128), width=2)

        # Draw label if present
        if self.label:
            try:
                # Basic text drawing, default font
                d.text((10, 10), self.label, fill=(0,0,0,255))
            except Exception:
                pass

        return img
