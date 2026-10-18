# Change log

**Status: complete through Stage 1 documentation work.**

## 2026-10-18 — Reference inspection, no redesign

- Preserved all imported source files and root license; did not edit/reroute the PCB.
- Created this separate documentation/audit workspace; no approved ROXX schematic or PCB yet.
- Inventoried 101 tracked source files and extracted symbols, PCB pad nets, footprints/model paths, PDF text and pin workbook.
- Recorded single-MCU/two-IMU architecture, missing firmware proof, schematic/PCB reference mismatch, suspicious SPL06 strapping, DJI O3-specific power path, library portability and manufacturing-rule issues.
- Captured confirmed requirements, deliverable statuses and initial staged validation plan.
- Installed Python analysis dependencies in a workspace virtual environment outside the source repository. No KiCad executable was available; ERC/DRC and hardware tests not run.
- Next: Stage 2 official PX4/manufacturer-source research and proposed ROXX architecture. Architecture approval required before Stage 4 electrical implementation.

## 2026-10-18 — Stage 2 architecture and official-source research

- Accepted fixed custom ROXX/PX4/Pi5/OAK-D Lite/external GNSS/quad boundary without reopening product decision.
- Verified official NXT dual target on stable v1.17.0 and pinned main, with stable default/bootloader release assets. Added Stage 1 audit correction for upstream support and SPL06 address-selection intent.
- Recorded source discrepancies: clock constants, inherited tuning/battery count/identity and supply-check bypass, console and RC inversion behavior, stable/main reset and sensor classification differences.
- Proposed H743VIT6 LQFP100, dual BMI088 with separate LDOs, BMP388 internal I2C, four TIM1 motors, SD, buzzer/debug/LEDs; CAN/I2C/extra telemetry reserved optional. Procurement remains unresolved.
- Added complete generated 100-contact preliminary pin allocation; checked unique assignments and ST function membership. Explicit AF/DMA/peripheral concurrency gate remains.
- Added preliminary connector contracts, system and power diagrams, symbolic/assumption-labelled load and thermal calculations, Pi USB5A/PD/OAK USB load treatment and power-fault strategy.
- Added functional candidate BOM, decision matrix, detailed firmware adaptation/build plan, source registry, licensed source snapshots and third-party asset release gate.
- Original tracked source files remain unchanged. No KiCad schematic/layout or actual ROXX BSP created; no final routing, firmware build, ERC/DRC, bench or flight test performed.
