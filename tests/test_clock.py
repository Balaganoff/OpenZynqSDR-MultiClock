import json
import tempfile
import unittest
from pathlib import Path
from boot.select_clock import select

class ClockSelectionTests(unittest.TestCase):
    def test_rejects_unbuilt_profile(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            c = root / "clock.ini"
            c.write_text("[clock]\nadc_frequency_hz = 54000000\n")
            m = root / "manifest.json"
            m.write_text(json.dumps({"profiles": {"54000000": {"verified": False}}}))
            with self.assertRaisesRegex(ValueError, "not built/verified"):
                select(c, m, root)

    def test_validates_and_calculates_audio_rate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "fpga").mkdir()
            (root / "fpga/adc_40mhz.bit.bin").write_bytes(b"test-only")
            c = root / "clock.ini"
            c.write_text("[clock]\nadc_frequency_hz = 40000000\n")
            m = root / "manifest.json"
            m.write_text(json.dumps({"profiles": {"40000000": {"verified": True, "bitstream": "fpga/adc_40mhz.bit.bin", "cic1":238, "cic2":14}}}))
            self.assertAlmostEqual(select(c, m, root)["audio_sample_rate_hz"], 40000000 / (238*14))

if __name__ == "__main__":
    unittest.main()
