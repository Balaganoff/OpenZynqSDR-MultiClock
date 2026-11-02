# Upstream boot artifacts audit (2026-11-02)

User supplied the original build artifacts:

| Artifact | Contents | Result |
|---|---|---|
| boot_fat32.zip | BOOT.BIN, boot.scr, image.ub | Original FAT32 boot payload present |
| BOOT_bin_parts.zip | zynq_fsbl.elf, system.bit, system.dtb, u-boot.elf, bootgen.bif | FPGA and bootloader inputs present |
| arm_app.zip | websdr.bin, sdrdma.ko, scripts, libfdk-aac.so | ARM application binary present |
| samples.zip | Receiver test samples | Present |
| system8.dts | Original Linux device tree source | Present |
| sdrdma.ko | Compiled ARM DMA kernel module | Present |

**Blocking facts**:

1. Author's Readme explicitly says **ROOTFS is NOT published here now**. A self-contained bootable SD card image cannot be reliably created by simply concatenating these inputs.
2. BOOT.BIN contains the **original fixed FPGA bitstream**. The uploaded firmware does not read the proposed `sdr-clock.ini` configuration. A filename with a new config does not implement variable clock support.
3. The upload does **not** supply a generated Vivado project supporting runtime CIC changes, nor a validated FPGA build for arbitrary clock inputs.

## Next implementation criteria

- Rebuild FPGA project with runtime configuration registers for CIC or equivalent rate converter, preserving a single bitstream.
- Update Linux app with config parser, register writes, DDS and sample-rate plumbing, and a correctly filtered output resampler.
- Build via Vivado 2022.2 and create a rootfs with compatible kernel/modules; validate on hardware.
- Produce a real dual-partition SD disk image only when these steps succeed.

**Do not confuse boot partition payload archives with complete bootable SD disk images.**
