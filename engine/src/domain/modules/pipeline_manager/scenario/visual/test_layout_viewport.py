"""
Layout Manager Test: Coordinate Mapping Verification
=====================================================

Tests the CoordinateMapper's ability to correctly transform PSD layer
coordinates to viewport space with 1:1 aspect ratio centered layout.

Output: tests/outputs/Layout/
"""

import os
import sys
import unittest

# Path setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SRC_ROOT = os.path.join(PROJECT_ROOT, "src")
if SRC_ROOT not in sys.path:
    sys.path.append(SRC_ROOT)

# Domain Imports
# Utils
from PIL import Image, ImageDraw  # noqa: E402

# Adapters
from adapters.driven.psd_modeler.psdtools_parser_adapter import PsdToolsAdapter  # noqa: E402
from domain.modules.layout_manager import create_coordinate_mapper  # noqa: E402

# Local Utils
from domain.modules.pipeline_manager.scenario.visual.layout_test_utils import (  # noqa: E402
    create_centered_viewport,
    setup_output_dir,
)
from domain.value_objects.resource.media_output_path_value import MediaOutputPath  # noqa: E402

# Configuration
PSD_PATH = os.path.join(os.path.dirname(__file__), "../../../../../assets/Psd/test.psd")
VIEWPORT_SIZE = 1080


class TestLayoutViewport(unittest.TestCase):
    """Layout Manager Test: Coordinate Mapping Verification."""

    def setUp(self):
        """Setup output paths."""
        self.project_id = "test_project"
        self.media_path = MediaOutputPath(
            base_path=os.path.abspath(os.path.join(PROJECT_ROOT, "media")),
            project_id=self.project_id,
        )
        self.output_dir = str(self.media_path.visual_test_dir / "Layout")
        setup_output_dir(self.output_dir)

    def test_run_layout_manager(self) -> None:  # noqa: PLR0915
        """Main test: Load PSD and verify coordinate mapping."""
        print("=" * 60)
        print("LAYOUT MANAGER TEST: 1:1 Centered Format")
        print("=" * 60)

        # Load PSD
        psd_path = os.path.abspath(PSD_PATH)
        print(f"\n[1] Loading PSD: {psd_path}")

        if not os.path.exists(psd_path):
            self.fail(f"ERROR: PSD file not found at {psd_path}")

        psd_adapter = PsdToolsAdapter()
        world = psd_adapter.load(psd_path)

        print(f"    PSD Size: {world.width} x {world.height}")
        print(f"    Layers Found: {len(list(world.scene.iterate_all()))}")

        # Setup Viewport and Camera (1:1 Center)
        print(f"\n[2] Creating 1:1 Centered Viewport ({VIEWPORT_SIZE}x{VIEWPORT_SIZE})")
        viewport, camera = create_centered_viewport(world.width, world.height)

        print(f"    Camera Position: {camera.position}")
        print(f"    Camera Zoom: {camera.zoom:.4f}x")
        print(f"    Viewport Aspect: {viewport.aspect_ratio}")

        # Create Coordinate Mapper
        mapper = create_coordinate_mapper(camera, viewport)

        print(f"\n[3] Visible World Rect: {mapper.get_visible_world_rect()}")

        # Test 1: Render all layers with coordinate overlay
        print("\n[4] Rendering Coordinate Overlay...")

        # Create blank viewport canvas
        canvas = Image.new("RGBA", (VIEWPORT_SIZE, VIEWPORT_SIZE), (240, 240, 240, 255))
        draw = ImageDraw.Draw(canvas)

        # Draw grid for reference
        grid_step = VIEWPORT_SIZE // 10
        for i in range(0, VIEWPORT_SIZE + 1, grid_step):
            draw.line([(i, 0), (i, VIEWPORT_SIZE)], fill=(200, 200, 200, 128), width=1)
            draw.line([(0, i), (VIEWPORT_SIZE, i)], fill=(200, 200, 200, 128), width=1)

        # Draw center crosshair
        center = VIEWPORT_SIZE // 2
        draw.line([(center - 50, center), (center + 50, center)], fill=(0, 0, 0, 255), width=2)
        draw.line([(center, center - 50), (center, center + 50)], fill=(0, 0, 0, 255), width=2)
        draw.text((center + 5, center + 5), "CENTER", fill=(0, 0, 0, 255))

        # Color palette for layers
        colors = [
            (255, 0, 0, 255),  # Red
            (0, 200, 0, 255),  # Green
            (0, 100, 255, 255),  # Blue
            (255, 165, 0, 255),  # Orange
            (128, 0, 128, 255),  # Purple
            (0, 200, 200, 255),  # Cyan
        ]

        # Process each layer
        layers_list = list(world.scene.iterate_all())
        print(f"\n    Processing {len(layers_list)} layers:")

        report_lines = []
        report_lines.append("LAYOUT MANAGER COORDINATE MAPPING REPORT")
        report_lines.append("=" * 50)
        report_lines.append(f"PSD: {os.path.basename(psd_path)}")
        report_lines.append(f"PSD Size: {world.width} x {world.height}")
        report_lines.append(f"Viewport: {VIEWPORT_SIZE} x {VIEWPORT_SIZE} (1:1)")
        report_lines.append(f"Camera: pos={camera.position}, zoom={camera.zoom:.4f}x")
        report_lines.append("")

        for idx, layer in enumerate(layers_list):
            color = colors[idx % len(colors)]

            # World coordinates (from PSD)
            world_pos = layer.position
            world_bounds = layer.bounds

            # Transform to viewport
            viewport_pos = mapper.world_to_viewport(world_pos)
            viewport_bounds = mapper.world_rect_to_viewport(world_bounds)

            # Check visibility
            is_visible = mapper.is_visible(world_bounds)

            # Log
            log_line = (
                f"    [{idx}] {layer.name[:20]:<20} | "
                f"World: ({int(world_pos.x):>4}, {int(world_pos.y):>4}) -> "
                f"Viewport: ({int(viewport_pos.x):>4}, {int(viewport_pos.y):>4}) | "
                f"Visible: {is_visible}"
            )
            print(log_line)

            # Report
            report_lines.append(f"Layer [{idx}]: {layer.name}")
            report_lines.append(
                f"  World Position (center): ({int(world_pos.x)}, {int(world_pos.y)})"
            )
            report_lines.append(
                f"  World Bounds: x={int(world_bounds.x)}, "
                f"y={int(world_bounds.y)}, "
                f"w={int(world_bounds.width)}, h={int(world_bounds.height)}"
            )
            report_lines.append(
                f"  Viewport Position: ({int(viewport_pos.x)}, {int(viewport_pos.y)})"
            )
            report_lines.append(
                f"  Viewport Bounds: x={int(viewport_bounds.x):.0f}, "
                f"y={int(viewport_bounds.y):.0f}, "
                f"w={int(viewport_bounds.width):.0f}, h={int(viewport_bounds.height):.0f}"
            )
            report_lines.append(f"  Is Visible: {is_visible}")
            report_lines.append("")

            # Draw on canvas - bounding box in viewport space
            vb = viewport_bounds
            if vb.width > 0 and vb.height > 0:
                draw.rectangle(
                    [vb.x, vb.y, vb.x + vb.width, vb.y + vb.height], outline=color, width=3
                )

            # Draw center point
            vp_x, vp_y = int(viewport_pos.x), int(viewport_pos.y)
            r = 10
            draw.ellipse([vp_x - r, vp_y - r, vp_x + r, vp_y + r], fill=color)

            # Draw layer name
            draw.text((vp_x + 15, vp_y - 10), f"{idx}: {layer.name[:15]}", fill=color)

        # Save coordinate overlay image
        overlay_path = os.path.join(self.output_dir, "coordinate_overlay.png")
        canvas.save(overlay_path)
        print(f"\n    Saved: {overlay_path}")
        self.assertTrue(os.path.exists(overlay_path))

        # Test 2: Render actual layers to verify positioning
        print("\n[5] Rendering PSD Content with Coordinate Mapping...")

        # Create canvas with white background
        content_canvas = Image.new("RGBA", (VIEWPORT_SIZE, VIEWPORT_SIZE), (255, 255, 255, 255))

        # Render layers in z-order
        for layer in sorted(layers_list, key=lambda layer: layer.z_index):
            if not layer.visible or layer.is_group:
                continue

            if layer.image_data is None:
                continue

            # Get layer bounds in viewport
            viewport_bounds = mapper.world_rect_to_viewport(layer.bounds)

            # Resize layer image to match viewport scale
            scaled_w = max(1, int(viewport_bounds.width))
            scaled_h = max(1, int(viewport_bounds.height))

            try:
                layer_img = layer.image_data.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

                # Paste at viewport position
                paste_x = int(viewport_bounds.x)
                paste_y = int(viewport_bounds.y)

                # Alpha composite
                content_canvas.alpha_composite(layer_img, (paste_x, paste_y))

                print(
                    f"    Rendered: {layer.name} at "
                    f"({paste_x}, {paste_y}) size {scaled_w}x{scaled_h}"
                )

            except Exception as e:
                print(f"    Warning: Could not render {layer.name}: {e}")

        # Save content render
        content_path = os.path.join(self.output_dir, "psd_content_mapped.png")
        content_canvas.save(content_path)
        print(f"\n    Saved: {content_path}")
        self.assertTrue(os.path.exists(content_path))

        # Test 3: Save comparison with debug overlay
        print("\n[6] Creating Debug Comparison...")

        comparison = content_canvas.copy()
        debug_draw = ImageDraw.Draw(comparison)

        # Draw bounding boxes over rendered content
        for idx, layer in enumerate(layers_list):
            color = colors[idx % len(colors)]
            viewport_bounds = mapper.world_rect_to_viewport(layer.bounds)

            if viewport_bounds.width > 0 and viewport_bounds.height > 0:
                debug_draw.rectangle(
                    [
                        viewport_bounds.x,
                        viewport_bounds.y,
                        viewport_bounds.x + viewport_bounds.width,
                        viewport_bounds.y + viewport_bounds.height,
                    ],
                    outline=color,
                    width=2,
                )

        # Draw viewport center
        debug_draw.line(
            [(center - 30, center), (center + 30, center)], fill=(255, 0, 0, 255), width=2
        )
        debug_draw.line(
            [(center, center - 30), (center, center + 30)], fill=(255, 0, 0, 255), width=2
        )

        comparison_path = os.path.join(self.output_dir, "debug_comparison.png")
        comparison.save(comparison_path)
        print(f"    Saved: {comparison_path}")
        self.assertTrue(os.path.exists(comparison_path))

        # Save Report
        report_path = os.path.join(self.output_dir, "coordinate_report.txt")
        with open(report_path, "w") as f:
            f.write("\n".join(report_lines))
        print(f"\n    Report: {report_path}")
        self.assertTrue(os.path.exists(report_path))

        print("\n" + "=" * 60)
        print("LAYOUT MANAGER TEST COMPLETE")
        print("=" * 60)
        print(f"\nOutput Directory: {self.output_dir}")


if __name__ == "__main__":
    unittest.main()
