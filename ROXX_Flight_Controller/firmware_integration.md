# PX4 integration strategy — Stage 2

**Status: partial — verified upstream reference, proposed ROXX target; NO local build, boot or driver test.** Sources and exact SHAs: [sources.md](sources.md). Hardware contract: [interface_specification.md](interface_specification.md), [pin_allocation.csv](pin_allocation.csv).

## 1. What has actually been verified

Official PX4 stable **v1.17.0** at `d6f12ad1c4f70ad3230afd7d86e971421e02fef4` contains NXT dual board configs, H743VI NuttX defconfigs, H7 NuttX bootloader, bus/timer tables and sensor startup. GitHub release publishes both `hkust_nxt-dual_default.px4` and `hkust_nxt-dual_bootloader.px4`. Main `ddcaad...` also has target. This is stronger evidence than the imported README's empty build headings, but does NOT establish exact imported PCB revision matching, maintenance guarantee, local build success or ROXX compatibility.

Future own board directory: **`boards/roxx/fc-v1/`**; intended make targets **`roxx_fc-v1_default`**, **`roxx_fc-v1_bootloader`**. These are proposed names, **not existing targets or working commands yet**. Do not alias ROXX to `hkust_nxt-dual`, FMUv6C or another manufacturer's ID.

## 2. Source/BSP adaptation plan

| File / subsystem | Required ROXX work | Hardware trace |
|---|---|---|
| `default.px4board` | Cortex-M7/H743VI, choose only actual drivers; BMI088, BMP388, ADC, GPS, PWM/DShot, RC, MAVLink, logger, safety/estimator modules | Selected BOM and interface CSV |
| `bootloader.px4board` and `nuttx-config/bootloader/defconfig` | New USB identity, clocks, VBUS input and reset-safe GPIO, flash size/entry | H743 package; VBUS PD7; SWD/BOOT0 |
| `nuttx-config/nsh/defconfig`, Kconfig | Correct CPU, serial instances, watchdog implementation, DMA policies, SPI1/4/I2C1/SDMMC1/ADC1; optional buses disabled by default | Resource ledger in interface spec |
| `nuttx-config/include/board.h` | Rebuild clocks/AF macros from valid H7 configuration, active-HSE bypass, actual silicon VOS/flash latency; 48 MHz USB; UART pin AFs | 16 MHz PH0, 400 MHz initial objective |
| `board_dma_map.h` | Remove NOR SPI2 allocation; validate UART4 DMA; introduce sensor DMA only after driver support/timing proof | Proposed DMA admission budget, NOT frozen stream map |
| `src/board_config.h`, `init.c` | New LDO enables, PG/reset, status LEDs, ADC channels, VBUS, watchdog and safe output sequence; initialization and sensor power-cycle hooks | PD4/PD10, PE10, PC4/5, PD7, motor pins |
| `src/spi.cpp` | BMI088 devices on SPI1 and SPI4; second gyro CS changes **PC2→PC0**; correct DRDYs; no fitted SPI2 flash | Pin table, two independent IMU rails |
| `src/i2c.cpp` | I2C1 internal barometer; I2C4 external only if fitted. Use API for selected stable release, not main-only shared-bus calls | PB6/7 and PD12/13 |
| `src/timer_config.cpp` | Four TIM1 outputs only; TIM8 HRT reserved; TIM4 buzzer; no source eight-output claim | PE9/11/13/14, PD14 |
| `init/rc.board_sensors` | Start each BMI088 accel/gyro on intended bus, rotation from mechanical axes; `bmp388` internal I2C1 strapped address | Do not inherit `-R 2` until physical orientation is proven |
| `init/rc.board_defaults` | Deliberate serial, airframe and safety defaults; no hardcoded battery count, arbitrary tune or disabled supply check | No copying `CBRK_SUPPLY_CHK=894281`, BAT1_N_CELLS=4 or source gains |
| `src/hw_config.h`, `firmware.prototype` | Unique approved board ID + owned/allocated USB VID/PID, ROXX names, correct boot delay/recovery/flash sizing | Do not reuse upstream ID1013 / Matek descriptions |
| Linker scripts / parameter storage | Protect bootloader and final parameter erase sector; map DMA-accessible SRAM and stack/heap/ITCM/DTCM deliberately | STM32H743VI 2 MB flash and fragmented SRAM |
| SD init, manifest, reset hooks | Logging mount errors must not block safety logic without clear policy; brownout/power loss fault logs; optional external interface detection | SDMMC1 and test points |

Stage 2 has **not** copied these snapshots into a live firmware tree or claimed a working BSP. They are evidence under `research/`, with original licenses.

## 3. Safety-relevant source differences

* Stable NXT barometer startup is `spl06 -X -a 0x77 start`; I2C1 and I2C4 are externally classified. Main changes bus classification/start behavior. ROXX uses internal-only I2C1 and BMP388, so neither source script is copied verbatim.
* Main reset change [633af612, P3] changes remaining affected motor outputs to driven-low reset states; stable reference has older behavior. Review/backport applicable fix into both application and bootloader; external pulldown/default-safe hardware must protect the interval before firmware executes. Test actual ESC startup with props removed.
* Source clock header has HSI/range inconsistencies; do not use successful artifact publication to waive clock review. Verify oscillator bypass, HSI=64 MHz specification, PLL input/VCO, prescalers, NuttX interpretation and USB clock on hardware. Initial 400 MHz recommendation is arithmetic only until RM/errata reviewed.
* Stable NXT sets `CONFIG_WATCHDOG=y`, but no inspected `CONFIG_STM32H7_IWDG` setting was established. Audit actual lower-half/init/arming and petting path; watchdog must reset on blocked flight tasks, not remain alive because an unrelated low-priority loop still pets it.
* NXT reset/peripheral-reset hooks do not provide real sensor-rail resets. ROXX must implement and test rail control without GPIO back-powering.
* Stable NXT linker application region begins **0x08020000**, length **1792 KiB**, ending **0x081E0000**; init reserves last **128 KiB** parameter sector at 0x081E0000. Candidate reuse of this layout requires explicit erase bounds/bootloader image reservation review; ROXX map not frozen.

## 4. Preliminary serial role mapping

NXT enables USART1/2/3, UART4/5, USART6, UART7/8. Device enumeration is derived from enabled NuttX instances and must be confirmed after configuring ROXX; these proposed names preserve that order through UART7.

| ROXX role | MCU | Proposed device | Configuration intent |
|---|---|---|---|
| GPS1 | USART1 PA9/10 | `/dev/ttyS0` | GNSS driver, module-specific protocol/baud, no assumed compass |
| TELEM1 radio | USART2 PD5/6 | `/dev/ttyS1` | MAVLink GCS stream; selected radio baud/load |
| TELEM3 optional | USART3 PD8/9 | `/dev/ttyS2` | Disabled until fitted; preserve peripheral slot if enumeration consistency needs it |
| TELEM2 companion | UART4 PB9/8 | `/dev/ttyS3` | Dedicated MAVLink2, initial 921600 8N1, suitable buffers/rate budget |
| RC | UART5 PB13/12 | `/dev/ttyS4` | Receiver-specific RC input protocol, inversion and return telemetry |
| Console | USART6 PC6/7 | `/dev/ttyS5` | NSH/service only, not exposed as MAVLink |
| ESC telemetry optional | UART7 PE7/8 | `/dev/ttyS6` | Selected compatible ESC UART protocol only |

These ROXX roles deliberately **differ** from NXT `default.px4board`: source GPS2 is ttyS2, TEL1 ttyS1, TEL2 ttyS3, TEL3 ttyS6, TEL4 ttyS7. Do not infer UART number from TELEM name or inherited connector silk. Disabling UART instances can renumber later device nodes; inspect generated config and test every port.

### MAVLink / GNSS / RC commissioning

* Assign exactly one MAVLink instance's `MAV_n_CONFIG` to ROXX TELEM2 and set corresponding serial baud (`SER_TEL2_BAUD` in applicable PX4 configuration). Use onboard/companion mode appropriate to selected release; confirm actual parameter enum values in that release instead of pasting numeric IDs. Instance index `n` is not hardcoded. Set MAVLink2 and stream rate budget; log packet errors. No simultaneous console, DDS or other driver ownership on UART4.
* Pi GPIO14 TX→FC RX, GPIO15 RX←FC TX and GND only. Disable serial console on the selected Pi5 UART and verify actual OS overlay/device node. A 3.3 V loopback and scope test precede MAVLink. Exact Pi image/overlay remains unresolved, not an assertion that Pi4 `ttyAMA0` instructions work unchanged.
* GNSS driver on GPS1 with module-approved baud/protocol/autoconfiguration; verify reconnect, configuration persistence, valid fix and time. PPS pin is reserved only; driver, timestamp latency and HRT capture support must be implemented/tested if required. No automatic compass support from serial GNSS.
* RC protocol chosen with actual receiver. Confirm native UART inversion in PX4/NuttX, idle voltage, bidirectional telemetry and power-loss behavior. Do not globally disable RC failsafes to make bench communications work.
* Configure four actuator functions through PX4 control allocation and verify motor order and rotation without props. Select timer-group PWM/DShot rate after ESC compatibility check; no inherited `PWM_MAIN_TIM0=-4` assumption. Bidirectional DShot is a separate implementation/test gate.
* Configure offboard-loss timeout/action (`COM_OF_LOSS_T` and release-appropriate action settings), RC loss, data-link loss, GNSS/estimator and low-battery actions. Test each with representative position/heading availability; choose explicit pilot takeover/arming policy. A Pi reboot must not auto-rearm or silently reacquire unsafe authority.

## 5. Reproducible build and update plan — NOT executed

Reference-only commands, to run in an **independent PX4 workspace**, never by switching this hardware repository's session branch:

```sh
git clone --recursive https://github.com/PX4/PX4-Autopilot.git /path/to/px4-reference
cd /path/to/px4-reference
git checkout d6f12ad1c4f70ad3230afd7d86e971421e02fef4
git submodule update --init --recursive
# Install the pinned revision's documented toolchain/build dependencies.
make hkust_nxt-dual_default
make hkust_nxt-dual_bootloader
# After reviewed ROXX BSP exists (not yet):
# make roxx_fc-v1_default
# make roxx_fc-v1_bootloader
```

Record exact compiler/CMake/Ninja/Python versions, submodule SHAs and build logs; inspect flash/RAM/map and warnings. Reference build proves only software toolchain/config compilation. ROXX acceptance requires app+bootloader builds, safe GPIO waveforms, first boot, drivers and timing under concurrent SD/MAVLink/ESC load.

First programming through SWD after current-limited rail checks; read silicon ID/revision, flash sizes, program bootloader and verify. Then test custom PX4 USB update/QGC recovery without identity collision, interrupted upload/power loss, BOOT0/ST ROM recovery and watchdog/NRST. ROM-supported interfaces and oscillator/USB conditions must be checked against current ST bootloader documentation before claiming DFU recovery. Do not flash NXT bundled bootloader binary into ROXX.

## 6. Firmware verification ledger

| Evidence | Result |
|---|---|
| Official stable/main target and stable release assets | Verified by GitHub API |
| Source pin/bus/timer/driver comparison | Reviewed; discrepancies recorded |
| ST package function membership / duplicate pin allocation | Script PASS; limited structural check |
| Reference build / ROXX target build | **Not run / not implemented** |
| Driver behavior, DMA concurrency, watchdog, bootloader recovery | **Untested** |
| Hardware compatibility / flight readiness | **Not established** |

Upstream inclusion requires unique identity, maintained port and physical validation/flight evidence per [D1]. Legal adaptation of BSD PX4 code is permissible with notices; NuttX/submodule licenses must be retained separately in actual firmware distribution. Upstream software licensing is not permission to clone commercial PCB CAD.
