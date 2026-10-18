# Validation plan and actual results

**Status: partial — initial stage gates; no hardware qualification performed.**

## Test ledger — 2026-10-18

| Check | Actual result | Boundary |
|---|---|---|
| Original-file inventory | 101 tracked source files hashed | ZIP not independently available |
| Native schematic/PCB structural parse | Successful; 137 PCB footprints; 14 non-power schematic references absent on PCB | Not net equivalence or ERC/DRC |
| Local PCB model path resolution | All KIPRJMOD references exist | Standard libraries and model accuracy unchecked |
| PDF extraction/workbook inspection | Three PDFs extracted; workbook sheets inspected | Not complete visual datasheet audit |
| KiCad CLI availability | Not found in PATH | ERC/DRC **not run**, no pass claimed |
| Firmware / simulation / physical / flight tests | Not performed | No compatibility/safety certification |

## Required staged validation gates

1. **Schematic/datasheet audit:** independent review of every selected MPN, symbol pin, footprint, strap, clock, reset/boot, rail rating, power-off I/O injection, sensor orientation, connector and protection path. Link findings to schematic reference and firmware pin definitions. Specialist electrical review needed.
2. **ERC/DRC:** run supported KiCad CLI on approved new design; retain raw reports, tool version and exact revision. Refill zones and check schematic/PCB net parity. Disposition every error/warning; do not hide unconnected or power errors. Criteria must reflect approved fabrication stack-up.
3. **Manufacturing:** assembler DFM/DFA review, BGA escape/stencil/reflow/X-ray requirements, solder-mask/paste/courtyard, drill/edge/screw/cable clearances, BOM lifecycle and supply-chain verification. Manual inspection and possibly X-ray required.
4. **Current-limited power-on:** propellers removed and ESC motor power disconnected; inspect resistance/polarity first. Use bench supply, DMM, oscilloscope and thermal measurement. Validate each rail, startup/inrush, enable/reset ordering and brownout at approved source limits before attaching Pi/ESC. Determine test limits from final design, not invented currents.
5. **MCU bring-up:** SWD identification/erase/program/verify; clocks/reset cause, bootloader, USB update and recovery; watchdog fault injection; startup outputs must remain safe. Debug probe and logic analyzer required.
6. **Sensors/GNSS:** identity registers, sample rates, DRDY timing, axes/rotation, noise under load, barometer pressure response, logging, GNSS configuration/fix and loss detection. Calibrated reference and vibration/thermal equipment as needed.
7. **ESC outputs:** logic-analyzer measurements first; motor tests **without propellers**, approved ESC protocol and signal voltage, all channels independently mapped; verify reset/boot/disarm and corrupted-command behavior. Do not test unknown wiring live.
8. **RC/telemetry:** electrical qualification, protocol/frame loss, reconnect, arming interlocks, configured link-loss actions and ground-station visibility.
9. **Pi MAVLink:** verify crossed 3.3 V-compatible TX/RX and ground, power-off isolation, configured ports/baud/message rates; quantify errors/latency under CPU and USB load. Prove FC does not rely on companion scheduling.
10. **OAK-D Lite/Pi:** supported USB cable, video+depth throughput, power peaks, thermal throttling, connector retention and mechanical field of view. Keep camera data out of FC MCU.
11. **Fault injection:** disconnect/reboot Pi, RC/GNSS/telemetry loss, sensor/bus stalls, SD faults, brownout, USB insertion and regulator overload. Validate configured offboard-loss and estimator/RC failsafes, reset-to-safe outputs and absence of Pi back-powering. Hazard review before each test.
12. **Controlled flight:** only after documented bench/ground acceptance, calibrated sensors and reviewer signoff. Follow applicable local operating rules, exclusion zone, competent pilot and staged low-risk envelope expansion. Log and inspect each run; never infer readiness from CAD or software checks alone.

Detailed numeric acceptance limits, instruments, test fixtures, owners, serial numbers and signed logs must be added after architecture/specification approval. No stage is passed by this plan merely existing.

## Stage 2 actual ledger — 2026-10-18

| Check | Actual result | Does not prove |
|---|---|---|
| Official PX4 stable/main API inspection | NXT dual target present at recorded SHAs; v1.17.0 assets list default + bootloader | Local successful build / exact imported board revision compatibility |
| Vendor package pin data | ST LQFP100 XML at pinned SHA; allocation generator PASS: 100 contacts, 64 assigned GPIOs, no duplicates, functions present | AF macro correctness / pad-map geometry / DMA / voltages |
| Imported circuit vs upstream | Barometer address-output intent resolved; firmware defaults and clock/reset risks recorded | Electrical signoff / real waveform correctness |
| Power and bandwidth arithmetic | Recalculated from stated formulas and explicit load assumptions | Worst-case actual MCU/SD/GNSS/ESC current or thermal adequacy |
| Full manufacturer pin/land-pattern audit | Incomplete; PDF page-access limits documented | Footprint release approval |
| Original source preservation | Recheck hashes and git diff before turn completion | Safety or firmware compatibility |
| Build/ERC/DRC/lab/flight | Not performed | No flight-readiness claim |

### Stage 2 turn-end automated checks (actual)

- **PASS:** regenerated 100-contact table; 64 unique assigned GPIOs and all assigned function names in pinned ST XML. No NuttX AF/DMA verification implied.
- **PASS:** SHA-256 comparison for all 101 imported tracked files; `git diff --exit-code` excluding new ROXX directory returned 0.
- **PASS:** research snapshot manifest hashes matched.
- **PASS:** all relative Markdown deliverable links resolved.
- **Arithmetic cross-check:** provisional FC scenario 1.12710 A at 5.2 V; example RGB+depth stream 101.376 MB/s. Input assumptions remain unqualified.
