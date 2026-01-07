
import unittest  # noqa: PLR0913, PLR0912
import sys
import os

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../')))

from domain.value_objects.geometry.vector_value import Vector2  # noqa: PLR0913, PLR0912
from domain.value_objects.geometry.rect_value import Rect
from domain.entities.camera_entity import CameraEntity
from domain.entities.viewport_entity import ViewportEntity
from domain.modules.layout_manager.coordinate_mapper_module import CoordinateMapper

class TestCoordinateMapping(unittest.TestCase):
    """
    Unit Test: CoordinateMapper
    Fungsi: Memastikan translasi koordinat World -> Viewport akurat.
    """

    def test_center_mapping_1to1(self) -> None:
        """Test: Center World harus mapping ke Center Viewport pada zoom 1.0"""
        # World 1000x1000
        # Viewport 100x100
        # Camera di 500,500

        viewport = ViewportEntity(100, 100)
        camera = CameraEntity(position=Vector2(500, 500), zoom=1.0)

        # Mapper logic:
        # offset = screen_center - (camera_pos * zoom)
        # screen_pos = (world_pos * zoom) + offset

        mapper = CoordinateMapper(camera, viewport)

        # Test Point: World Center (500, 500)
        world_center = Vector2(500, 500)
        screen_center = mapper.world_to_viewport(world_center)

        # Harusnya di Viewport Center (50, 50)
        self.assertAlmostEqual(screen_center.x, 50.0)
        self.assertAlmostEqual(screen_center.y, 50.0)

    def test_zoom_mapping(self) -> None:
        """Test: Zoom 2.0 harus membuat objek 2x lebih besar/jauh."""
        viewport = ViewportEntity(100, 100)
        camera = CameraEntity(position=Vector2(0, 0), zoom=2.0)
        mapper = CoordinateMapper(camera, viewport)

        # World Point (10, 10)
        # Dengan zoom 2x, jarak dr center (0,0) di viewport harusnya 20px
        # Center viewport ada di (50, 50)
        # Jadi (10*2 + 50, 10*2 + 50) = (70, 70)

        world_pos = Vector2(10, 10)
        screen_pos = mapper.world_to_viewport(world_pos)

        self.assertAlmostEqual(screen_pos.x, 70.0)
        self.assertAlmostEqual(screen_pos.y, 70.0)

    def test_rect_mapping(self) -> None:
        """Test: Mapping Rect (Bounding Box)."""
        viewport = ViewportEntity(100, 100)
        camera = CameraEntity(position=Vector2(0, 0), zoom=1.0)
        mapper = CoordinateMapper(camera, viewport)

        # Rect di world (0, 0, 10, 10)
        # Di viewport center (50, 50), jadi x=50, y=50, w=10, h=10
        world_rect = Rect(0, 0, 10, 10)
        screen_rect = mapper.world_rect_to_viewport(world_rect)

        self.assertAlmostEqual(screen_rect.x, 50.0)
        self.assertAlmostEqual(screen_rect.y, 50.0)
        self.assertAlmostEqual(screen_rect.width, 10.0)
        self.assertAlmostEqual(screen_rect.height, 10.0)

if __name__ == '__main__':
    unittest.main()
