# Architecture decision matrix — Stage 2

**Status: partial / recommendation awaiting critical-pin, sourcing and power-envelope approval.** The decision to make a **new custom ROXX PX4 board** is final and is not reopened here. Evidence keys resolve in [sources.md](sources.md). Qualitative development-effort assessments are engineering judgment, not measured benchmarks.

## MCU / reference strategy

| Candidate | Verified PX4 evidence | Resources / assembly / availability | Effort and maintainability | Disposition |
|---|---|---|---|---|
| STM32H743VIT6, LQFP100 | NXT BSP explicitly selects H743VI [P2]; ST package functions verified [ST1] | 2 MB flash; ~1 MB SRAM distributed across domains; same logical H743VI core, larger footprint than BGA but inspectable leads; stock quote pending | Lowest conceptual divergence from verified NXT buses; package and changed peripherals still require own BSP, full pin audit and firmware test | **Recommend Rev A** |
| Imported STM32H743VIH6, TFBGA100 | Exact MCU family/variant in NXT files [P2] | Same class resources; compact 8 × 8 mm package; custom footprint/X-ray/escape increases manufacturing burden; stock pending | Avoids logical chip change, but does not resolve upstream clock/reset/identity issues | Prefer only if strict size constraint justifies BGA |
| H743 larger LQFP144/176 implementation | Durandal explicitly selects H743II in stable defconfig [P5]; package and full config still need review | More routable I/O and flow-control options, larger board; procurement pending | More freedom for later CAN/extra ports; adds area without clear Rev A need | Backup if mechanical envelope permits and feature set grows |
| STM32H753-class FMUv6 architecture | FMUv6X stable defconfig explicitly selects H753II [P5]; FMUv6C instead selects H743VI. Neither is an electrically compatible substitute target | Same M7 performance class with additional features; exact package/resources must be verified before substitution | Mature reference pattern; full sensor/power/pin adaptation still needed; commercial CAD licensing cannot be inferred from PX4 software | Viable product alternative, not lowest-effort starting point |
| STM32F7-class PX4 target | Official porting guide describes F7 ports [D1]; no exact F7 target assessed here | Less headroom for modern PX4 features than selected H743; no quote | Reduces future firmware margin without a demonstrated cost/availability advantage | Do not select |
| H7 newer families / i.MX RT class | No exact target/chip combination audited in this stage | Potential performance benefit is not proof of driver/BSP fit | New package/power/debug/resource review; avoid adding porting risk solely for MHz | Defer |

**Clock recommendation:** 16 MHz active HSE oscillator, initial CPU target **400 MHz**, not copied NXT PLL constants. Configure valid PLL input/VCO/prescalers/flash latency/voltage scale from RM0433 and exact silicon errata. Example arithmetic only: 16/4 × 200 /2 = 400 MHz, VCO 800 MHz. This is NOT an approved register configuration. USB needs a verified 48 MHz source independent of guessing CPU divisors.

## Sensor choices

| Configuration | PX4 evidence | Benefit | Cost/risk | Decision |
|---|---|---|---|---|
| 2 × BMI088, separate SPI buses and separate LDOs | Explicit selected driver and startup for both on NXT [P2/P4] | Least new driver integration; vibration-oriented part [M2]; independent bus/rail fault handling | Two same-type IMUs do not give design-diverse redundancy; 4 DRDY pins; vendor stock widget currently zero/unreliable without quotes | **Recommend conditionally**, procurement gate before schematic freeze |
| 1 × BMI088 | Same verified driver | Simplest bring-up / less area | No sensor failover; poorer product fault tolerance | Bring-up population option only, not default product |
| BMI088 + ICM-42688-P | Stable official `icm42688p` driver directory and FMUv6C default driver selection verified [P4/P5]; imported footprint presence alone was not evidence | Sensor/vendor diversity, smaller second IMU | Different CS/IRQ/FIFO handling and calibration; availability, complete manufacturer datasheet and chosen bus config not audited here | Preferred fallback study if BMI088 supply cannot be secured; not approved pin-compatible substitution |
| BMP388 barometer on dedicated internal I2C1 | Stable `bmp388` driver + common barometer Kconfig verified [P4] | Public manufacturer datasheet; removes ambiguous SPL06 nomenclature/address logic | Lifecycle/stock not independently qualified; package is NOT assumed pin-compatible with SPL06 | **Recommend one**, subject to procurement and full footprint audit |
| Retain SPL06 | Explicit stable startup and source [P2/P4] | Upstream implementation exists | Restricted third-party PDF provenance, vendor availability unresolved; mode/address review required | Do not carry into Rev A by default |
| BMP390 / DPS310 / BMP581 | Some alternatives selected in common driver menu [P4]; exact part/driver binding requires review | Potential supply/lifecycle alternatives | No automatic drop-in, datasheet/current/driver audit incomplete | Procurement-triggered alternatives only |

No candidate has been declared currently stocked or release-qualified merely from a manufacturer page.

## Feature scope

| Mandatory Rev A | Optional, reserve resources but DNP / defer |
|---|---|
| MCU, clock/reset/BOOT0, hardware IWDG integration, SWD/NRST/VTref, safe outputs | Separate external watchdog IC if safety objective requires independent monitor |
| Two IMUs with distinct CS/DRDY/buses and separate low-noise LDOs | Third IMU, second barometer: defer |
| One barometer, microSD logging; internal-flash parameter sector | External NOR/FRAM: defer, do not mislabel NOR |
| Four direct timer ESC outputs with ground reference, power-off safe interface | Four extra motor outputs: defer; bidirectional DShot/ESC UART only after ESC verification |
| GNSS UART and protected module power, dedicated Pi UART without power pin, RC UART, one telemetry UART, USB FS | GNSS PPS reserve; optional second telemetry UART and I2C expansion |
| Status LEDs and timer-driven external passive buzzer MOSFET interface | One CAN1 footprint/connector DNP pending need, exact transceiver and firmware; no CAN-FD claim from merely having controller |
| Protected external regulated FC supply input; separate Pi/PDB power engineering | Redundant external FC supply connector/ideal-OR DNP if actual power redundancy justified |

## Engineering decisions requiring user input (not product-architecture reopening)

1. Approve proposed H743 **LQFP100** + dual BMI088 + BMP388 baseline and the reviewed critical pin table, contingent on real procurement quotes. If supply fails, authorize heterogeneous sensor re-evaluation before CAD.
2. Provide battery chemistry/cell count/min/max, ESC and motor part numbers (or defer raw-battery power and motor-current qualification explicitly). Approve **external FC power module + independent Pi converter**, instead of raw battery conversion next to FC sensors. A 4S–6S ordinary LiPo envelope is only a proposal, not an assumed aircraft specification.
3. Identify GNSS and receiver models/protocols plus telemetry radio load; these fix power switches, level adaptation, harnesses and RC inversion. For reliable autonomous heading, decide whether to qualify an external compass or alternative heading source; no onboard compass is mandatory.
4. Specify board/mounting envelope and assembler constraints. Rev A default recommendation is six layers, no imported 33 × 27 mm constraint. CAN is DNP unless a concrete peripheral needs it.

These inputs block schematic freeze, not documentation progress. No final routing is authorized by these recommendations.
