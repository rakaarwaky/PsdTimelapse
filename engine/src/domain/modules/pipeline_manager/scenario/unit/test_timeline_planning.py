import unittest  # noqa: PLR0913, PLR0912
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../')))

from domain.modules.script_director.planners.smart_timeline_planner_module import plan_smart_timeline  # noqa: PLR0913, PLR0912
from domain.entities.layer_entity import LayerEntity
from domain.value_objects.geometry.rect_value import Rect
from domain.value_objects.animation.action_type_value import ActionType

class TestTimelinePlanning(unittest.TestCase):
    """
    Unit Test: ScriptDirector
    Fungsi: Memastikan logic pembuatan timeline (urutan, durasi) benar.
    """

    def create_mock_layer(self, id, z=0):
        return LayerEntity(
            id=id, name=f"Layer_{id}", z_index=z,
            bounds=Rect(0,0,100,100), visible=True
        )

def test_empty_timeline(self) -> None:
    """Test: Planning tanpa layer harus return timeline kosong (atau exception handled)."""
    timeline = plan_smart_timeline([], 1000, 1000)
    self.assertEqual(len(timeline.actions), 0)
    self.assertEqual(timeline.total_duration, 0.0)

def test_staggered_timing(self) -> None:
    """Test: Layer-layer harus punya waktu mulai yang bertingkat (tidak barengan)."""
    layers = [
        self.create_mock_layer("layer1", "type1"),
        self.create_mock_layer("layer2", "type2")
    ]
    timeline = plan_smart_timeline(layers, 1000, 1000)
    self.assertEqual(len(timeline.actions), 2)
    self.assertEqual(timeline.total_duration, 2000.0)

def test_staggered_timings(self) -> None:
    """Test: Staggered Timings: Actions should be sorted by layer Z (asumsi default staggered menaik)."""
    self.create_mock_layer("L1", 1)
    self.create_mock_layer("L2", 2)
    self.create_mock_layer("L3", 3)
    layers = [
        # Disable exclusion to test behavior of ALL provided layers
        timeline = plan_smart_timeline(layers, 1000, 1000, exclude_bottom_layer=False)

        # Urutkan action berdasarkan layer Z (asumsi default staggered menaik)
        actions = sorted(timeline.actions, key=lambda a: a.start_time)

        self.assertEqual(len(actions), 3)
        # Action kedua harus mulai setelah action pertama (atau ada jeda)
        self.assertGreater(actions[1].start_time, actions[0].start_time)
        self.assertGreater(actions[2].start_time, actions[1].start_time)

        print(f"✓ Staggered Timings: {[a.start_time for a in actions]}")

    def test_exclude_background(self) -> None:
        """Test: Option exclude_bottom_layer harus skip layer paling bawah."""
        bg = self.create_mock_layer("BG", 0)
        fg = self.create_mock_layer("FG", 1)

        timeline = plan_smart_timeline([bg, fg], 1000, 1000, exclude_bottom_layer=True)

        # Harusnya cuma ada action untuk FG
        # BG mungkin ada tapi type NONE atau tidak ada sama sekali di list

        bg_actions = [a for a in timeline.actions if a.layer_id == "BG" and a.action_type != ActionType.NONE]  # noqa: PLR0913, PLR0912
        fg_actions = [a for a in timeline.actions if a.layer_id == "FG"]
        self.assertEqual(len(bg_actions), 0, "Background should not have animation action")
        self.assertGreater(len(fg_actions), 0, "Foreground must have animation")

if __name__ == '__main__':
    unittest.main()
