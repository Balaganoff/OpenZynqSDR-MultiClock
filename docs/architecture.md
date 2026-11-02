# Runtime arbitrary oscillator architecture (WIP)

## Hard distinction

The software in `clocking/plan.py` calculates *candidate* CIC ratios and DDS values for arbitrary frequencies. No FPGA integration has been made yet. Never claim a clock is hardware supported from this calculation alone.

## Proposed hardware/software interface

1. System runs from a stable Zynq PS clock, independent of external ADC oscillator where possible.
2. On boot, parse `adc_frequency_hz` from config before enabling reception.
3. Program safe (disabled) runtime decimation parameters in PL, and reset CIC integrators/comb state when new settings latch.
4. Start ADC clock domain, synchronize control/acknowledgement across CDC boundaries, and enable RX only after PLL/MMCM lock and reset release (when applicable).
5. Compute tuning and waterfall NCO words with the actual ADC sample rate; publish that rate to browser/UI.
6. Convert actual decimated sample rate to the required output rate with a correctly filtered rational resampler.
7. Validate PL timing, external ADC clock electrical characteristics, CIC intermediate widths, Nyquist and analog anti-alias filters on actual hardware.

## Required upstream audit

- Trace `ADC_CLOCK_HF`, `ADC_CLOCK_VHF`, `adc_clock_hz` through frequency-scale, channel DDC and waterfall.
- Trace `SOUND_CIC1_DECIM` / `SOUND_CIC2_DECIM` and all actual Verilog/BD CIC configurations.
- Confirm Xilinx CIC IP supports runtime rates; if not, replace IP or synthesize max-rate configuration with runtime-controlled stage counters.
- Examine ADC clock distribution, Zynq FCLK dependencies, generated-clock constraints and MMCM input minimums.
- Examine DMA throughput and baseband buffer sizing for variable rates.

## Measurable acceptance tests

- Same bitstream hash for external clock values 39.5 and 54 MHz.
- Reference RF at 7.100 MHz tunes and labels correctly for each.
- Voice and waterfall operate with correct timebase after each boot.
- No violations in static timing over the supported clock range.
- Fail with explicit error if outside the *hardware-validated* range.
