import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from boot.select_clock import load_plan
from clocking.plan import dds_word, make_plan

class ClockTests(unittest.TestCase):
    def test_arbitrary_39500000(self):
        plan = make_plan(39_500_000)
        self.assertEqual(plan.adc_hz, 39_500_000)
        self.assertLess(abs(plan.baseband_hz - 12_000), 12)
        self.assertEqual(Fraction(plan.pcm_resample_up, plan.pcm_resample_down) *
                         Fraction(plan.adc_hz, plan.cic1*plan.cic2), 48_000)

    def test_multiple_not_presets(self):
        for hz in (39_500_000, 40_000_000, 50_000_000, 54_000_000, 61_440_000, 51_234_567):
            with self.subTest(hz=hz):
                self.assertEqual(make_plan(hz).adc_hz, hz)

    def test_dds(self):
        self.assertEqual(dds_word(10_000_000, 40_000_000), 1 << 30)
        with self.assertRaises(ValueError):
            dds_word(20_000_000, 40_000_000)

    def test_invalid_frequency(self):
        with self.assertRaises(ValueError):
            make_plan(0)
        with self.assertRaises(ValueError):
            make_plan(100_000_000)

    def test_file(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "clock.ini"
            f.write_text("[clock]\nadc_frequency_hz=39500000\n")
            self.assertEqual(load_plan(f).adc_hz, 39_500_000)

if __name__ == "__main__":
    unittest.main()
