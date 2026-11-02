#!/usr/bin/env python3
"""Calculate a runtime clock plan from config; does NOT program real FPGA registers."""
import argparse
import configparser
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clocking.plan import make_plan

def load_plan(path: Path):
    config = configparser.ConfigParser()
    if not config.read(path):
        raise ValueError(f"Missing clock config: {path}")
    freq = config.getint("clock", "adc_frequency_hz")
    target = config.getint("clock", "audio_target_hz", fallback=12_000)
    return make_plan(freq, target)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config/sdr-clock.ini"))
    args = parser.parse_args()
    plan = load_plan(args.config)
    print(json.dumps(plan.as_dict(), indent=2))
    print("PLANNING ONLY: FPGA register interface and clock-domain validation not implemented.", file=__import__("sys").stderr)

if __name__ == "__main__":
    main()
