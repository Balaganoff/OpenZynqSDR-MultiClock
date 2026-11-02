# OpenZynqSDR MultiClock

**Status: early scaffold. NOT a bootable SD image and NOT hardware-validated.**

Goal: one SD image for Antminer S9 / Zynq-7010 with user-selectable external ADC oscillator: **40, 50, 54 or 61.44 MHz**. Initial implementation selects a *prebuilt frequency-specific FPGA profile* at boot.

Edit `config/sdr-clock.ini`:
```ini
[clock]
adc_frequency_hz = 54000000
```

At this stage, the selector **fails closed** until a corresponding bitstream has been built and verified. Changing the configuration alone does NOT make an unmodified upstream FPGA design support new clock rates.

## Upstream

- [OpenZynqSDR_HW](https://github.com/iliasam/OpenZynqSDR_HW): Vivado 2022.2 project, AD9226 ADC board
- [OpenZynqSDRApp](https://github.com/iliasam/OpenZynqSDRApp): Linux application and DMA kernel driver
- [Author clock-change wiki](https://github.com/iliasam/OpenZynqSDR_HW/wiki)

Upstream currently hardcodes 40 MHz in `init/clk.h` and CIC1=238, CIC2=14 in `zynq/peri.h`. These must match FPGA implementation. Upstream source is not yet vendored.

## Milestones

1. Reproduce baseline 40 MHz bitstream + functioning boot image.
2. Audit PL clock domains, PLL constraints, CIC and sample-rate assumptions.
3. Synthesize, validate and package profiles for 50 / 54 / 61.44 MHz.
4. Integrate early boot profile selection with FPGA loading, compatible software and error reporting.
5. Hardware-test tuning accuracy, audio, waterfall and startup on Antminer S9 + AD9226.
6. Publish reproducible SD image, only after validation.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 boot/select_clock.py --root .
```

Second command intentionally fails until a validated bitstream is installed.

## Hardware

Nyquist limits for 40/50/54 MHz: 20/25/27 MHz respectively. Actual useful receive bandwidth requires suitable input filtering. Verify clock level, clock path and PL timing before attaching an oscillator.
