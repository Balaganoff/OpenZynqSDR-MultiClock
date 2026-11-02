# OpenZynqSDR MultiClock

**Goal: one bootable SD image + one FPGA bitstream, with user-configurable external ADC sampling clock.**

> Development only. No FPGA implementation or boot image is validated yet.

## Primary requirement (no frequency presets)

The operator specifies the *actual oscillator frequency* in `config/sdr-clock.ini`:

```ini
[clock]
adc_frequency_hz = 39500000
```

Examples: 39.5, 40, 50, 54, 61.44 MHz, and other physically supported frequencies within a range **to be established by timing analysis and hardware testing**. No separate FPGA bitstream and no source rebuild for each value.

At startup the application must compute NCO/DDC tuning words from the configured sampling clock; select appropriate CIC rates and post-decimation/resampling for audio; correct waterfall bins, frequency display and protocol metadata. The FPGA must expose runtime-configurable CIC decimation (or another equivalent digital design), safely apply filter and pipeline changes, and support clock/reset domains over the validated input range. A fixed-rate output clock may require resampling.

### Acceptance criteria

1. Boot the **same SD image and FPGA bitstream** with 39.5 MHz then 54 MHz external clocks, changing only the configuration file, and receive correctly on both.
2. Verify frequency accuracy, audio rate, waterfall calibration, stability and simultaneous receivers against a signal generator.
3. Reject unsupported values with a useful diagnostic rather than silently tuning incorrectly.
4. Document oscillator input electrical requirements and measured frequency limits.

### Current state

- `boot/select_clock.py` and `profiles/manifest.json` are a **discarded preset-profile proof of concept** committed during initial setup. **Do not use them as the target architecture.** They will be replaced with a universal runtime clock parameter implementation.
- The tracked tests cover only that obsolete proof of concept, not actual SDR functionality.
- No frequency-flexible PL design has been synthesized or tested; no bootable image exists.

### Upstream

- [OpenZynqSDR_HW](https://github.com/iliasam/OpenZynqSDR_HW) (Vivado 2022.2 / Zynq-7010)
- [OpenZynqSDRApp](https://github.com/iliasam/OpenZynqSDRApp) (Linux application and driver)
- [Clock frequency wiki](https://github.com/iliasam/OpenZynqSDR_HW/wiki)

Upstream software uses hardcoded `ADC_CLOCK_HF` and `ADC_CLOCK_VHF` values, while `SOUND_CIC1_DECIM` and `SOUND_CIC2_DECIM` are constants. These are not sufficient to support arbitrary clock frequencies by changing a configuration value: the PL and Linux application must be reworked together.

## Build strategy

1. Audit the FPGA clocking architecture and timing constraints, distinguish ADC input clock from Zynq processing clocks.
2. Inventory all fixed sampling and decimation assumptions in FPGA and Linux software.
3. Implement safe runtime clock/decimation configuration, while keeping a single FPGA bitstream.
4. Build and boot a baseline image, then test multiple arbitrary frequencies with unchanged binary artifacts.
5. Publish an image only after verification on real Antminer S9 + AD9226 hardware.
