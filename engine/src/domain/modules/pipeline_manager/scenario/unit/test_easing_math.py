
import unittest
import sys
import os

# Setup path to import engine/src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../')))

from domain.value_objects.animation.easing_curve_value import EasingCurve, EasingType

class TestEasingMath(unittest.TestCase):
    """
    Contoh Unit Test:
    Hanya mengetes LOGIKA MATEMATIKA. 
    Tidak ada gambar yang dirender, tidak ada file yang ditulis.
    Cepat (< 0.01 detik).
    """

    def test_linear_easing(self):
        """Test Linear: Input harus sama dengan Output."""
        curve = EasingCurve(EasingType.LINEAR)
        
        self.assertAlmostEqual(curve.apply(0.0), 0.0)
        self.assertAlmostEqual(curve.apply(0.5), 0.5)
        self.assertAlmostEqual(curve.apply(1.0), 1.0)
        print("✓ Linear Math OK")

    def test_ease_in_quad(self):
        """Test Ease In: Input kecil -> Output lebih kecil lagi (lambat di awal)."""
        curve = EasingCurve(EasingType.EASE_IN)
        
        # t=0.5 -> 0.5 * 0.5 = 0.25 (Quad)
        # Mari kita cek apakah nilainya < 0.5
        result = curve.apply(0.5)
        self.assertLess(result, 0.5) 
        print(f"✓ Ease In Logic OK: Input 0.5 -> Output {result}")

    def test_overshoot_logic(self):
        """Test Logic 'Overshoot' (mantul sedikit)."""
        # Bayangkan animasi yang kebablasan sedikit lalu balik lagi
        curve = EasingCurve(EasingType.EASE_OUT_BACK, overshoot=1.70158)
        
        # Di t=1.0 seharusnya tetap 1.0 (posisi akhir pas)
        self.assertAlmostEqual(curve.apply(1.0), 1.0)
        
        # Tapi di tengah jalan mungkin > 1.0 
        # (ini susah dicek visual, gampang dicek angka)
        
if __name__ == '__main__':
    unittest.main()
