"""Pure clock arithmetic. This is NOT a hardware programmer or validated FPGA design."""
from dataclasses import asdict, dataclass
from fractions import Fraction

# Engineering planning limits only, not validated silicon limits.
PLANNING_MIN_HZ = 1_000_000
PLANNING_MAX_HZ = 65_000_000
DDS_BITS = 32
PCM_HZ = 48_000

@dataclass(frozen=True)
class ClockPlan:
    adc_hz: int
    cic1: int
    cic2: int
    baseband_hz: float
    target_hz: int
    pcm_hz: int
    pcm_resample_up: int
    pcm_resample_down: int
    nyquist_hz: float

    def as_dict(self):
        return asdict(self)

def dds_word(tune_hz: int, adc_hz: int, *, bits: int = DDS_BITS) -> int:
    """Unsigned DDS phase increment, with nearest-integer rounding.

    Tune range must be in [0, Nyquist) to avoid ambiguous aliases.
    """
    if not 0 <= tune_hz < adc_hz / 2:
        raise ValueError("Tune frequency must be in [0, ADC Nyquist)")
    return (tune_hz * (1 << bits) + adc_hz // 2) // adc_hz

def make_plan(adc_hz: int, target_hz: int = 12_000,
              *, first_stage_min: int = 8, first_stage_max: int = 1024,
              second_stage_min: int = 2, second_stage_max: int = 256) -> ClockPlan:
    """Find integer CIC stages approximating target; correct final PCM rate by resampling.

    Values are *proposed*, not known-safe for the upstream CIC architecture.
    Runtime programmable hardware and bandwidth/alias rejection must be implemented.
    """
    if type(adc_hz) is not int or not PLANNING_MIN_HZ <= adc_hz <= PLANNING_MAX_HZ:
        raise ValueError("ADC clock outside planning range (NOT a hardware guarantee)")
    if type(target_hz) is not int or not 4_000 <= target_hz <= 96_000:
        raise ValueError("Invalid target baseband rate")
    best = None
    for c2 in range(second_stage_min, second_stage_max + 1):
        desired = adc_hz / (target_hz * c2)
        for c1 in {int(desired), int(desired) + 1}:
            if first_stage_min <= c1 <= first_stage_max:
                err = abs(Fraction(adc_hz, c1*c2) - target_hz)
                score = (err, abs(c1-238), c2, c1)
                if best is None or score < best[0]:
                    best = (score, c1, c2)
    if best is None:
        raise ValueError("No decimation available within proposed hardware limits")
    _, c1, c2 = best
    base = Fraction(adc_hz, c1*c2)
    rate = Fraction(PCM_HZ, 1) / base
    return ClockPlan(adc_hz, c1, c2, float(base), target_hz, PCM_HZ,
                     rate.numerator, rate.denominator, adc_hz/2)
