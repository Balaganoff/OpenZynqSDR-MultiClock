#!/usr/bin/env python3
"""Select a prebuilt, verified FPGA clock profile. Does not program the FPGA."""
import argparse
import configparser
import json
from pathlib import Path

def select(config_path: Path, manifest_path: Path, root: Path) -> dict:
    cfg = configparser.ConfigParser()
    if not cfg.read(config_path):
        raise ValueError(f"Configuration missing: {config_path}")
    frequency = cfg.getint("clock", "adc_frequency_hz")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    profile = manifest["profiles"].get(str(frequency))
    if profile is None:
        raise ValueError(f"Unsupported ADC frequency: {frequency} Hz")
    if not profile.get("verified"):
        raise ValueError(f"Profile {frequency} Hz is not built/verified yet")
    if not isinstance(profile.get("cic1"), int) or not isinstance(profile.get("cic2"), int):
        raise ValueError("Missing CIC decimation parameters")
    bitstream = root / profile["bitstream"]
    if not bitstream.is_file():
        raise ValueError(f"Missing bitstream: {bitstream}")
    return {"adc_frequency_hz": frequency, "bitstream": str(bitstream),
            "cic1": profile["cic1"], "cic2": profile["cic2"],
            "audio_sample_rate_hz": frequency / (profile["cic1"] * profile["cic2"])}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, default=Path("config/sdr-clock.ini"))
    p.add_argument("--manifest", type=Path, default=Path("profiles/manifest.json"))
    p.add_argument("--root", type=Path, default=Path("."))
    args = p.parse_args()
    print(json.dumps(select(args.config, args.manifest, args.root), indent=2))

if __name__ == "__main__":
    main()
