# Imported hardware audit — Stage 1

**Status: partial; repository inventory and structural inspection complete, electrical correctness awaiting verification.**  
Audit date: 2026-10-18. Source: repository checkout at `fad7860aa12501ed6f7dff6d967b4c9bf1c30f9f` (`NxtDual` reference). Original files were not edited.

## 1. Scope and evidence

The named ZIP is not present in this workspace. This audit covers **all 101 tracked files in the imported checkout**, not an independently verified ZIP extraction. `audit/source_manifest.csv` records paths, sizes and SHA-256 hashes. No claim is made about absent archive contents, external repositories, hidden test history, or production hardware.

Inspected structurally: schematic, PCB, project JSON, custom symbol library, footprint/model references, CubeMX configuration and Excel pin workbook. Extracted text from all three PDFs; viewed all four PNG renderings. Library/model files are inventoried, but their geometry, pin numbering and third-party provenance have **not** been exhaustively datasheet-audited. PDF text extraction is not equivalent to a visual electrical review.

| Resource | Finding |
|---|---|
| `NxtFC-DUAL/NxtPX4.kicad_sch` | KiCad schematic format 20230121; single A2 sheet, title NxtPX4, date 2023-03-03, revision `V1.0。1`; 213 placed symbol units, 211 unique references including power symbols |
| `NxtFC-DUAL/NxtPX4.kicad_pcb` | Four copper layers; 137 footprints, 1,087 segments, 106 track arcs, 296 vias, 431 zone objects (not necessarily 431 independent power pours) |
| `NxtFC-DUAL/NxtPX4.kicad_pro` | Rules/net classes and UI settings; no firmware target |
| `project_lib/NxtPX4_Symbol.kicad_sym` | Custom MCU, sensor, regulator, logic and artwork symbols; schematic also embeds symbols |
| `project_lib/NxtPX4.pretty/` | Custom footprints, including unused sensor/regulator alternatives; presence does not mean fitted |
| `project_lib/3D_Model/` | STEP mechanical models; exact footprint/model correspondence and rights unverified |
| `NxtPX4.pdf` | One-page schematic export identifies KiCad 7.0.9; not proof of synchronization with current native files |
| `production/.../NxtPX4-*-Courtyard.pdf` | Two single-page assembly/courtyard exports; not a complete fabrication release |
| `NXTVersion2.0/*.ioc`, `*.xlsx` | CubeMX pin/config reference and workbook; no compiled PX4 implementation |
| Root README | Firmware/bootloader/configuration headings have no actual instructions; remote image references are not self-contained documentation |
| Four root PNG files | CAD renderings, not test results or evidence of manufactured boards |

There are no tracked PX4/NuttX board sources, bootloader source/binaries, CI builds, Gerber/drill release, pick-and-place release, complete manufacturer BOM, measured power budgets, ERC/DRC reports, or flight-test logs in the supplied checkout.

## 2. Actual reference architecture

**One MCU with two IMUs.** No second flight-control MCU or separate I/O processor is represented. Do not interpret the repository name as dual flight-controller redundancy.

| Subsystem | Observed implementation | Reuse assessment |
|---|---|---|
| MCU | U11 STM32H743VIH6, custom 100-ball BGA footprint; three symbol units refer to the same MCU | H7-family concept is useful; exact package, silicon revision, pinout and PX4 support require independent verification |
| IMUs | U14/U15 BMI088 on separate named SPI buses, separate gyro/accelerometer CS and data-ready nets | Useful bus-separation pattern; both powered from `Core_3V3`, so not independent power fault domains; orientation and drivers unverified |
| Barometer | U13 SPL06, I2C1-named nets, powered from `Core_3V3` | Reassess exact part/driver and interface-mode strapping before reuse |
| Clocking | Y1 SG-210STF oscillator into PH0, Y2 32.768 kHz crystal | Workbook says 16 MHz HSE; precise oscillator ordering code/frequency must be reconciled with datasheet and actual populated part |
| Storage | J10 microSD via SDMMC1; U16 W25Q128JVS via SPI2-named nets | Useful logging provision; W25Q128 is SPI NOR, **not FRAM**, despite FRAM net names and workbook heading |
| Main outputs | Four TIM1 channels at J6; four additional TIM2/TIM3 channels at J8 | Timer grouping is useful; actual PWM/DShot/DMA capability is not proven by labels |
| GNSS | J3 USART1 plus external I2C4, `System_5V`, GND | External GNSS pattern useful; no GNSS receiver or compass fitted; harness is not automatically compatible with any standard GPS cable |
| Companion | J5 UART4 TX/RX, `System_5V`, GND | UART concept useful; **do not power Raspberry Pi 5 from this connector** |
| RC | J7 UART5 TX and SBUS; U19 SN74LVC1G86 XOR with MCU-controlled inversion input | Receiver-dependent; default inversion, voltage tolerance and boot state need audit |
| Other serial | J4 USART2; J2 USART3/SBUS with camera power; J11 UART8 plus SWD | Useful resource reference; role labels differ among PCB silk, workbook and connector values |
| Debug/recovery | SWD signals at J11, boot pushbutton, NRST net | J11 includes 5 V, not a demonstrated 3.3 V VTref; reset is not brought to this connector. Add deliberate production debug/recovery provision |
| Expansion | J12 SPI3 and auxiliary GPIO; I2C4 at J3; USB FS at J1 | No CAN transceiver present. J12 has no numbered ground pin; grounded mounting pads do not constitute a suitable harness ground |
| Annunciation | RGB/status LEDs; schematic text mentions buzzer | A complete independently verified buzzer driver/output is not established by that text |

### Reference MCU resource map (not a ROXX allocation)

Workbook/CubeMX describe SPI1 on PA5/6/7 and SPI4 on PE2/5/6 for IMUs; SPI2 PD3/PB14/PC3 with CS PD4 for storage; SPI3 PB3/PB4/PB2 for expansion. I2C1 PB6/PB7 serves barometer; I2C4 PD12/PD13 is external. TIM1 PE9/11/13/14 supplies primary outputs; TIM2 PB10/11 and TIM3 PB0/1 supply auxiliary outputs. USB FS uses PA11/12, SWD PA13/14, SDMMC1 PC8–12/PD2, battery ADCs PC4/PC5.

Workbook UARTs: USART1 PA9/10; USART2 PD5/6; USART3 PD8/9; UART4 PB9/8; UART5 PB13/12; UART7 PE8/7; UART8 PE1/0. Workbook calls USART6 PC6/7 unsupported by external hardware. Its IMU accel data-ready entry contains literal `s`, not a valid pin. Treat these documents as fallible references. Pin-to-pad CSV is stronger evidence of PCB assignment, but still not a schematic connectivity comparison.

The `.ioc` selects STM32H743VIHx and Cube FW_H7 V1.11.1. Recorded RCC CPU/SYSCLK values include **10 MHz**, not an operational PX4 clock configuration. CubeMX configuration is neither NuttX configuration nor a PX4 port. DMA allocation, DShot timer DMA, cache coherency, interrupt priorities, EXTI conflicts, driver timing and watchdog operation remain unproven.

## 3. Imported connector pinouts

**PCB pad-net extraction only. Not approved wiring instructions.** Pin numbers are footprint numbers, not left-to-right cable views. Logic nets are MCU-domain signals; 5 V power next to them does not establish 5 V logic tolerance.

| Connector | Numbered contacts in order |
|---|---|
| J2 `DJIO3` | 1 CAM_9V; 2 GND; 3 USART3_TX; 4 USART3_RX; 5 GND; 6 SBUS |
| J3 `GPS` | 1 GND; 2 System_5V; 3 USART1_TX; 4 USART1_RX; 5 EX_I2C4_SCL; 6 EX_I2C4_SDA |
| J4 `UART2` | 1 GND; 2 System_5V; 3 USART2_TX; 4 USART2_RX |
| J5 `Upper computer connector` | 1 GND; 2 System_5V; 3 UART4_TX; 4 UART4_RX |
| J6 `ESC` | 1 battery-current ADC input; 2 UART7_RX; 3 TIM1_CH1; 4 TIM1_CH2; 5 TIM1_CH3; 6 TIM1_CH4; 7 VCC_BAT; 8 GND |
| J7 `Upper computer connector` | 1 GND; 2 System_5V; 3 UART5_TX; 4 SBUS (through U19 to UART5_RX) |
| J8 `PWM_AUX` | 1 GND; 2 TIM3_CH4; 3 TIM3_CH3; 4 TIM2_CH3; 5 TIM2_CH4 |
| J11 `Debug` | 1 GND; 2 System_5V; 3 UART8_TX; 4 UART8_RX; 5 SCLK (SWCLK intent); 6 SWDIO |
| J12 `AuxGPIO` | 1 AUX3_PA4; 2 AUX2_PC1; 3 AUX1_PC0; 4 EX_SPI3_MOSI; 5 EX_SPI3_MISO; 6 EX_SPI3_SCK |

J1 is USB-C USB2.0 with FS D+/D− nets and individual 5.1 kΩ CC resistors. Protection, impedance, shield strategy, VBUS sensing and backfeed behavior need verification. J9 exists in the schematic but not the PCB. See `audit/reference_pcb_pad_nets.csv` for full data, including power ICs and MCU ball nets. Connector family, mating part, retention, current rating and cable pin numbering remain unverified.

## 4. Imported power architecture — intent, not qualification

```text
VCC_BAT -- Q1 AP40P05 reverse-polarity circuit --> VCC_24V
   | TVS D3 SMF30CA                               |
   |                                             +-- U1 MP9943 + L1 --> System_5V
   |                                             +-- U4 MP9943 + L2 --> CAM_9V --> DJI O3
USB VBUS / system-source steering (D5/D7) --> System_4V5
                                                +-- U2 RT9013 --> Core_3V3 --> MCU + both IMUs + barometer
                                                +-- U3 RT9013 --> Periph_3V3 --> microSD + SPI NOR
External ESC current-sense signal --> PC5 ADC input
Battery divider/filter --> PC4 ADC input
```

Names such as `VCC_24V`, `CAM_9V`, and schematic annotations “2S–6S”, “3 A”, “500 mA” describe **reference intent**, not ROXX requirements or verified ratings. No ROXX battery voltage or available current is established.

* U4 feedback includes R16 with an ambiguous range/“3k for 12V” value, while the rail is called CAM_9V and assembly text mentions 12 V. Resolve the fitted resistor/output voltage rather than trusting a net name.
* Diode-steered source topology needs explicit forward-drop, USB backfeed and brownout analysis. `System_4V5` is a nominal name, not measured voltage.
* The MCU and IMUs share U2. Splitting core and peripheral rails helps load isolation but does not remove digital noise or common-mode failure from the IMU supply.
* Current measurement appears to rely on an external ESC analog output; there is no demonstrated calibrated onboard motor-current shunt/amplifier chain. ADC range, transfer function and fault protection must be specified.
* TVS standoff/clamping, MOSFET VGS/VDS, capacitors, regulator absolute maximum and battery/ESC transients need coordinated review. A 30 V TVS label alone does not prove downstream protection.
* No regulator load, peak/startup budget, stability/derating calculation, copper thermal model or input-transient measurement was supplied. No regulator is accepted as adequate from this audit.
* DJI O3 power is not an OAK-D Lite interface or a Raspberry Pi supply. OAK-D Lite must connect to the Pi via supported USB. Remove or redesign this ROXX-inapplicable subsystem rather than adapting its cable blindly.
* High-current motor power belongs to ESC/PDB paths, not these FC connectors/traces. Common signal reference is necessary, but Pi/ESC load return currents must not flow through FC sensor ground paths.

## 5. Electrical and manufacturing findings

| ID | Priority | Evidence / risk | Required disposition |
|---|---|---|---|
| AUD-01 | Release blocker | No PX4 target, bootloader implementation, build artifact or startup log | Select a pinned official PX4 baseline and prove custom BSP/driver/timer configuration; do not claim compatibility yet |
| AUD-02 | Release blocker | 14 non-power references in schematic absent from PCB | Reconcile intent and schematic/PCB synchronization before derivative work |
| AUD-03 | High | SPL06 PCB pin 2 CSB is explicitly unconnected; pin 5 SDO is named Baro_I2C1_DR | Verify authoritative SPL06 datasheet/mode/address straps. Schematic text says CSB to VDDIO for I2C and SDO strap determines address; current mapping is suspicious. Do not declare a confirmed defect without exact part verification |
| AUD-04 | High | Camera rail alternate feedback values and DJI O3-specific circuit | Replace/remove for ROXX; independent Pi power engineering required |
| AUD-05 | High | No current/thermal/transient/connector qualification | Build actual budgets and protection coordination once aircraft power is known |
| AUD-06 | High | Missing project symbol/footprint library tables; `.gitignore` ignores `*sym-lib-table` and `*fp-lib-table` | New ROXX project needs explicitly tracked project-local tables; embedded schematic symbols/PCB footprints do not make source libraries portable |
| AUD-07 | High | J11 exposes 5 V, lacks explicit 3.3 V VTref and NRST | Use clearly keyed debug connector/test points and verify probe power compatibility |
| AUD-08 | Medium | W25Q128 mislabeled FRAM, ambiguous MCU oscillator frequency | Correct documentation; verify memory technology, driver and clock configuration |
| AUD-09 | High | Sensor footprints, orientation matrices and DRDY wiring unqualified | Check each pad against manufacturer drawing; record board axes and test driver rotations |
| AUD-10 | High | Model/library provenance not separately documented | Preserve BSD notice; obtain rights for third-party models, symbols and footprints before redistribution |
| AUD-11 | High | No recorded receiver/ESC electrical or protocol specification | Establish voltage, idle state, inversion, startup output safety, DMA mapping and failsafe tests |
| AUD-12 | Medium | J12 no numbered GND contact; no CAN transceiver | Redesign expansion connector and deliberately resource CAN if approved |

Absent references: `C25`, `J9`, `FID1–FID3`, `TP3`, `TP4`, `TP6–TP8`, `TP10`, `TP11`, `TP13`, `U17`. Some may intentionally be artwork or unused mechanical/test items, but C25/J9 need explicit electrical disposition. All 137 PCB footprint references occur in the schematic and their **value strings** agree. This is **not** net equivalence, pad-map verification or proof of no missing connections.

PCB outline bounds are X=90…123 mm, Y=60…87 mm (**33 × 27 mm**). Four M2-named mounting footprints are present; hole drill, plated status, screw clearances and actual mounting pitch require mechanical review. Four-layer stack-up lists 35 µm copper per layer and three 0.274 mm dielectric layers, with 0.01 mm masks: total ~0.982 mm including masks. This is file data, not an approved fabrication stack-up or controlled-impedance specification.

Project minimum clearance/track width is 0.1 mm; minimum copper-edge clearance is **0 mm**. One Signal net-class via is 0.25/0.1 mm diameter/drill, while minimum through-hole drill is 0.15 mm and microvias are disabled. Class settings are not evidence of actual used geometries, but need reconciliation with fabrication capabilities. `netclass_patterns` is empty, so named classes do not establish applied per-net constraints. DRC exclusions list is empty, but several checks are ignored (including dangling vias); this is not a passed DRC. BGA escape and small 0201 parts require assembler capability, paste/reflow review and inspection, potentially X-ray for BGA joints.

All `${KIPRJMOD}` model paths referenced by the PCB resolve to existing files in this checkout. Standard model paths mix KiCad 6 and 7 environment variables and were not resolved against installed model libraries. At least some models warrant dimensional review (e.g. oscillator source footprint vs referenced model). 3D models are mechanical aids, never electrical validation.

## 6. Licensing and attribution

Root `LICENSE` is **BSD 3-Clause**, copyright **2023 Peize-Liu**. It permits redistribution/modification subject to retaining the copyright, conditions and disclaimer in source; reproducing them in binary distribution documentation/materials; and not using author/contributor names for endorsement without permission.

Retain the root license and give provenance for any copied circuits, symbols or layouts. Do not relabel original work as exclusively ROXX-authored. The root notice is useful evidence of repository licensing but is not proof the contributor owned every third-party STEP model, vendor-derived symbol, KiCad library item, or logo. No separate model provenance/license manifest was found. Do not copy original Nxt/HKU/HILAB artwork or signatures into ROXX branding. Conduct item-level rights review before distributing reused assets. This is an engineering license assessment, not legal clearance.

## 7. Reuse disposition

**Useful ideas, subject to independent verification:** H7-class real-time core, two separate IMU SPI buses, microSD logging, explicit CS/DRDY signals, external UART GNSS, dedicated companion UART, direct MCU timer ESC outputs, separate peripheral rail and accessible test points.

**Modify substantially:** package choice for assembly, sensor power isolation, clock/reset/watchdog strategy, barometer interface, debug pinout, all connectors/cable definitions, protection, battery sensing, power-source switching, layer stack-up and manufacturing rules.

**Replace or omit:** DJI O3 camera subsystem; any assumption the peripheral 5 V rail can power a Pi 5; ambiguous memory naming; source-specific logos; unverified firmware-support claims. No mandatory second MCU, onboard GNSS, compass or CAN expansion is inferred from the source.

## 8. Verification boundary / next gate

`kicad-cli` and `pdftotext` were not found in PATH. PDF extraction used pypdf instead. **ERC: not run. DRC: not run.** No KiCad GUI netlist comparison, firmware compilation, electrical simulation, device programming, power measurement, hardware test or flight test was performed. Extraction tools: Python, sexpdata, pypdf, openpyxl. Reproduction script is `tools/audit_reference.py`.

Proceed next to Stage 2: verify MCU/BSP and sensor choices against official pinned PX4 source and manufacturer datasheets, then propose ROXX architecture. Missing battery/ESC/motor/receiver/GNSS and mechanical requirements will be presented at Stage 3 only where they materially affect selection. **No schematic/PCB implementation is approved or started.**

## Stage 2 addendum — corrections from upstream evidence (2026-10-18)

The original Stage 1 results were limited to imported files. Official PX4 **does** have `boards/hkust/nxt-dual` on stable v1.17.0 and inspected main, and stable release assets include default firmware and bootloader. This resolves source-target existence in AUD-01, **not** ROXX build/hardware verification. Exact source SHAs and snapshots are in `sources.md` / `research/`.

AUD-03 is narrowed: firmware intentionally initializes **PB5 high as SPL06 address selection**, despite `Baro_I2C1_DR` net naming. The linked Goertek datasheet copy describes default I2C and an internal CSB pull-up. Therefore no-connect CSB and PB5 “DR” naming are **not confirmed electrical defects**. Full original-part qualification remains incomplete; restricted third-party document provenance is a product concern. Stage 2 recommends BMP388 instead.

Richtek's current manufacturer page lists **RT9013 EOL**; MPS describes MP9943 as **3 A peak**, not a blanket 3 A continuous rating. Other newly found source issues (HSI/PLL header inconsistencies, supply-check bypass, inherited tuning/identity, console connector mismatch, version-dependent reset behavior) are detailed in `architecture.md` and `firmware_integration.md`. No imported design files were changed to address them.
