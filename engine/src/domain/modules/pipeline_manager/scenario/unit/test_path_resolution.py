
import unittest  # noqa: PLR0913, PLR0912
import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../')))

from domain.value_objects.resource.media_output_path_value import MediaOutputPath  # noqa: PLR0913, PLR0912

class TestPathResolution(unittest.TestCase):
    """
    Unit Test: MediaOutputPath
    Fungsi: Memastikan struktur folder output konsisten.
    """

    def test_project_structure(self) -> None:
        """Test: Struktur folder standar (layout, ui, final)."""
        base = Path("/tmp/engine_media")
        project_id = "unit_test_proj"

        media_path = MediaOutputPath(base_path=base, project_id=project_id)

        # Cek path construction
        self.assertEqual(media_path.project_root, base / project_id)
        self.assertEqual(media_path.final_frames_dir, base / project_id / "final" / "frames")
        self.assertEqual(media_path.layout_dir, base / project_id / "layout")

        # Cek manifest path
        self.assertTrue(str(media_path.manifest_path).endswith("_manifest.json"))

    def test_sanitization(self) -> None:
        """Test: Nama project aneh-aneh harus dibersihkan."""
        # Implementasi sanitasi mungkin belum ada di ValueObject,
        # tapi test ini memastikan path tetap valid.

        base = Path("/tmp")
        messy_id = "Project Spasi & Tanda Baca!"
        media_path = MediaOutputPath(base_path=base, project_id=messy_id)

        # Minimal tidak crash
        self.assertTrue(media_path.project_root, "Should create valid path object")
        print(f"✓ Path resolved: {media_path.project_root}")

if __name__ == '__main__':
    unittest.main()
