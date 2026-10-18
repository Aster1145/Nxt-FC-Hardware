# Requirements baseline

**Status: partial — user requirements captured; electrical and product specification not frozen.**

| ID | Confirmed requirement | Verification / later artifact |
|---|---|---|
| R01 | New ROXX FC, intended PX4 real-time core with supported BSP, bootloader and drivers | Pinned source, target build, startup and HIL/bench logs |
| R02 | MCU owns IMU acquisition, stabilization, motor control and immediate configured failsafes | Timing and companion-loss tests |
| R03 | IMU and barometer; at least four independent ESC controls | Datasheet/pin/driver audit; sensor and propeller-free motor tests |
| R04 | External GNSS; no mandatory onboard GNSS or compass | Module-specific electrical and protocol qualification |
| R05 | Raspberry Pi 5 via dedicated supported UART/MAVLink interface | Pinout, safe power-off behavior, packet and link-loss tests |
| R06 | OAK-D Lite connects directly to Pi by supported USB, never through FC MCU | USB bandwidth/power/thermal/mechanical integration test |
| R07 | Four BLDC motors, one 4-in-1 or four ESCs; actual compatibility must be verified | Motor/ESC/battery datasheets, protocol test, current measurements |
| R08 | Independently engineered Pi supply, regulated FC/sensors, battery V/I measurement, protection and grounding | Actual peak/startup/thermal budget and power fault tests |
| R09 | RC, telemetry, debug and appropriately scoped expansion | Resource matrix, connector specification and failsafe tests |
| R10 | Real KiCad design after approval, traceable net/pin/firmware assignments and manufacturing package | ERC/DRC, net equivalence, assembly review and production tests |
| R11 | Preserve imported originals; all new work in this directory; respect licenses | Source hash manifest, git diff and attribution review |
| R12 | No flight readiness claim based only on drawings/checks/3D models | Completed staged physical validation and controlled-flight signoff |

## Unresolved inputs — not assumptions

Battery chemistry/cell count and minimum/maximum/transient voltage; motor model and operating envelope; ESC model/rating/control protocol/telemetry; power distribution and current measurement source; GNSS model/power/logic/connector/PPS; receiver model/protocol/logic/inversion; telemetry radio; aircraft mounting envelope and cable clearances; environmental range; redundancy objective; production volume/assembler capability and cost targets.

These are a decision backlog, not a demand for answers before completing Stage 2. No imported 2S–6S annotation, 24 V net name, 3 A claim, physical outline, connector pinout or sensor choice is adopted as a ROXX requirement. No exact MCU, board target, regulator, connector, layer count or sensor has been selected yet.

## Stage 2 update — 2026-10-18

**Status: partial; fixed product decisions final, detailed engineering approval pending.**

The user reconfirmed that ROXX is a NEW custom PX4 PCB with Pi 5, OAK-D Lite directly via USB, external GNSS and four ESC-driven BLDC motors. These choices are final, not options for reconsideration. Flight stabilization/sensor processing/motor control/essential failsafes remain on FC. Imported NXT hardware is a reference, never mandatory final architecture.

| New requirement / proposal | State | Verification gate |
|---|---|---|
| Verify `hkust_nxt-dual` in official PX4 | **Complete source/release verification** | Exists stable v1.17.0 and inspected main; no local build/flight verification |
| New board-specific firmware target/identity | Mandatory product engineering | Proposed `roxx_fc-v1`; new board ID and USB VID/PID not allocated |
| H743VIT6 LQFP100; two BMI088; one BMP388 | Recommended, not approved final parts | Procurement, silicon/datasheet/land-pattern review, updated BSP |
| All MCU contacts budgeted | Preliminary table complete | 100-contact CSV validation passes vendor function membership; AF/DMA/electrical checks pending |
| Four TIM1 direct motor channels | Recommended critical allocation | ESC electrical/protocol selection; reset-safe and DShot/PWM testing |
| Separate FC and Pi regulated paths | Mandatory separation; external FC converter recommended | Battery and load specs, protection, efficiency/thermal/startup calculations |
| Aircraft battery range | **Unresolved** | Proposed ordinary 4S–6S LiPo for discussion only; actual battery/motor/ESC data required |
| Pi interface supply | 5.1V / 5A capability recommendation from official Pi requirement | Correct PD recognition/cable and measured total load, camera USB peaks |
| No power on companion UART connector | Proposed mandatory harness safety | Verify 3.3V logic and rail-off injection protection |
| Buzzer, LEDs, SD, debug/recovery | Rev A recommended mandatory | MPN/power/timer/firmware tests |
| CAN, external I2C, second telemetry, PPS | Optional reserved / DNP | Enable only for actual peripheral requirement; no untested function claim |
| CAD/firmware licensing manifest | Mandatory | See licensing_review.md; no third-party CAD assumed cleared |

The earlier statement “no exact MCU ... selected yet” describes the Stage 1 baseline only; Stage 2 now makes a **preliminary selection** above, not a manufacturing release. Stage 2 documents, sources, preliminary BOM, power equations and conflict ledger exist; final routing is not authorized. Missing component currents and battery ratings remain unknown rather than silently filled with reference-board numbers.
