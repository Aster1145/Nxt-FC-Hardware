# Preliminary interfaces and MCU allocation — Stage 2

**Status: partial — proposed pin/connector contract, awaiting review; no routed netlist.** All signal directions below are relative to FC. MCU selected for proposal: **STM32H743VIT6 LQFP100**. This is not the imported BGA ball map. Evidence: [ST1, P2 in sources.md](sources.md).

## 1. Allocation authority and validation

[pin_allocation.csv](pin_allocation.csv) is the **complete 100-contact preliminary table**, including power/reset/VCAP/unassigned contacts. Generated from pinned ST XML by `python ROXX_Flight_Controller/tools/generate_pin_allocation.py`. Actual result: 100 distinct package contacts, 64 uniquely assigned GPIOs, all assigned vendor functions found in XML. This detects duplicate allocation/missing functions, **not** AF-number/NuttX-macro correctness, loading, signal integrity or DMA conflicts.

| Function / intended nets | MCU GPIOs | LQFP contacts (same order) | Peripheral / ownership |
|---|---|---|---|
| IMU1 SCK, MISO, MOSI | PA5, PA6, PA7 | 29,30,31 | SPI1; short onboard bus, no external devices |
| IMU1 gyro CS, accel CS | PA3, PA2 | 25,24 | GPIO output; pull up to IMU1 rail |
| IMU1 gyro DRDY, accel DRDY | PA1, PA0 | 23,22 | EXTI1, EXTI0 |
| IMU2 SCK, MISO, MOSI | PE2, PE5, PE6 | 1,4,5 | SPI4 |
| IMU2 gyro CS, accel CS | PC0, PC13 | 15,7 | GPIO output; **PC0 differs from NXT PC2** |
| IMU2 gyro DRDY, accel DRDY | PE3, PE4 | 2,3 | EXTI3, EXTI4 |
| IMU1/IMU2 LDO enables | PD4, PD10 | 85,57 | GPIO; reset default defined by pulls, see power sequence |
| Barometer SCL, SDA | PB6, PB7 | 92,93 | I2C1 internal only; no CS/IRQ MCU pin; strap BMP388 mode/address locally |
| GNSS TX, RX | PA9, PA10 | 68,69 | USART1, full duplex, module-dependent baud |
| GNSS PPS reserve | PA8 | 67 | Optional EXTI8, **not yet a PX4 PPS driver/timer-capture implementation** |
| Companion TX, RX | PB9, PB8 | 96,95 | UART4 dedicated MAVLink; no RTS/CTS in Rev A |
| RC TX, RX | PB13, PB12 | 52,51 | UART5, separate conductors; inversion/protocol confirmed after receiver selection |
| Telemetry1 TX, RX | PD5, PD6 | 86,87 | USART2 |
| Telemetry2 TX, RX | PD8, PD9 | 55,56 | Optional USART3, DNP connector |
| ESC UART telemetry RX / TX reserve | PE7, PE8 | 37,38 | UART7 optional; do not tie push-pull outputs from four ESCs together |
| Console TX, RX | PC6, PC7 | 63,64 | USART6 debug; TIM8 peripheral reserved for HRT, channel pins not used for PWM |
| USB D−, D+ | PA11, PA12 | 70,71 | USB OTG FS device; cannot also use PA11/12 CAN |
| USB VBUS sense | PD7 | 88 | GPIO via qualified divider/clamp; relocated from NXT PD0 |
| SWDIO, SWCLK, optional SWO | PA13, PA14, PB3 | 72,76,89 | Debug; no SPI3 external connector on these pins |
| ESC1,2,3,4 | PE9, PE11, PE13, PE14 | 39,41,43,44 | TIM1 CH1,2,3,4; shared timer protocol/rate group |
| Buzzer gate | PD14 | 61 | TIM4_CH3; passive buzzer + MOSFET driver; not SBUS inversion |
| Battery voltage/current scaled | PC4, PC5 | 32,33 | **ADC1 INP4/INP8**, not split across ADC1/ADC2 merely because original labels say so |
| SD data D0,D1,D2,D3,CK,CMD | PC8,PC9,PC10,PC11,PC12,PD2 | 65,66,78,79,80,83 | SDMMC1, 4-bit; card pull-ups to card-compatible rail |
| RGB red/green/blue | PD15,PD11,PB15 | 62,58,54 | Active-low GPIO, resistors set from LED current specifications |
| CAN1 RX/TX reserve | PD0,PD1 | 81,82 | FDCAN1; transceiver/termination DNP, software not enabled yet |
| External I2C SCL/SDA reserve | PD12,PD13 | 59,60 | I2C4 optional; not shared with onboard barometer |
| Core power-good monitor | PE10 | 40 | GPIO input, not used as TIM1 alternate function |
| HSE input / unused HSE output | PH0,PH1 | 12,13 | 16 MHz active oscillator into PH0; bypass-mode configuration mandatory; PH1 NC |
| Optional LSE in/out | PC14,PC15 | 8,9 | 32.768 kHz crystal DNP; pads must not be used as expansion GPIO |
| Reset / boot | NRST,BOOT0 | 14,94 | Supervisor/probe/button; pulldown BOOT0 and recovery access |
| VCAP1/2 | VCAP contacts | 48,73 | Each per ST capacitor requirement; **never external 3.3 V** |
| VDD / GND | VDD / VSS | 11,27,50,75,100 / 10,26,49,74,99 | Every contact connected/decoupled; see full CSV |
| Analog / backup power | VSSA,VREF+,VDDA,VBAT | 19,20,21,6 | Analog return/reference filtering; VBAT to core supply, no backup cell Rev A |

Unassigned GPIOs remain reserved; no net may be added without updating CSV, schematic and BSP. PC2_C/PC3_C are deliberately unused: do not assume ordinary digital behavior without configuring/auditing H7 analog switches.

### Peripheral / timing / DMA conflict ledger

* **EXTI:** IMU IRQs use lines 0,1,3,4, PPS line8. No port-multiplex collision among these. Do not add barometer interrupt on PA4/PB4: EXTI4 is already PE4.
* **TIM1:** only four primary motor outputs. All share timer period/mode; no mixing incompatible PWM/DShot protocols within group. PE13/14 alternative SPI4 pins are unavailable, so SPI4 must stay PE2/5/6.
* **TIM8:** HRT timebase, as NXT firmware uses; PC6/7 use USART6 AF, not HRT output pins. Do not enable TIM8 pin outputs. **TIM4:** buzzer only. **TIM2/3:** not advertised Rev A outputs; reserve until system/capture ownership review.
* **CAN:** PD0/1 avoids USB PA11/12, companion PB8/9 and RC PB12/13. Requires relocating VBUS sense to PD7 in bootloader AND app. Optional FDCAN clocks/bit timing/driver and standby behavior unimplemented.
* **SPI2/NOR omitted:** frees two DMA clients and pins; no source SPI2 DMA configuration should remain enabled without a fitted device. SPI3 omitted to keep SWO and reduce connector noise.
* **NXT actual DMA:** board_dma_map explicitly enables SPI2 and UART4 maps; defconfig enables SPI2 DMA and UART4 RX/TX DMA, **not SPI1/SPI4 DMA**. `_0`/`_1` macros and stale comments must be checked against pinned NuttX implementation; comments are not authoritative stream allocations.

Proposed DMA admission budget, **not executable DMA-map configuration**:

| Client | Planning controller / reserved stream capacity | Action before freeze |
|---|---|---|
| TIM1 DShot update | DMA1: one stream | Preserve timer DMA requirement; verify generated request/stream choice in PX4 io_timer implementation |
| SPI1 RX/TX | DMA1: two streams if enabled | First bring-up may retain interrupt/polled transfer; decide after measured CPU/jitter. No claim upstream enabled this |
| SPI4 RX/TX | DMA1: two streams if enabled | Verify request compatibility with same controller; allocate after TIM1; serialize same-bus transfers |
| UART4 RX/TX | DMA2: two streams | Continuous companion traffic; verify RX circular buffering/cache alignment and dynamic allocator masks |
| SDMMC1 | SDMMC IDMA, not assumed to consume DMA1/2 streams | Verify IDMA/cache-safe accessible RAM and card-write latency |
| ADC1 / I2C1 / other UARTs | No DMA initially | Bounded polling/IRQ; verify no RX loss under peak load |

Five planned DMA1 and two DMA2 clients fit nominal eight-stream/controller capacity, but **capacity is not a conflict proof**. Stream masks, request eligibility, runtime allocation, shared IRQ priorities and cache coherency remain blocked on BSP compilation and concurrency tests. Do not force arbitrary numeric stream macros from this table. DMA buffers must not be placed in inaccessible DTCM; use appropriate SRAM and cache maintenance per NuttX/PX4.

## 2. Proposed connector contracts (NOT imported pinouts)

Prefer keyed locking **JST-GH 1.25 mm** signal connectors (exact horizontal/vertical and MPN chosen after envelope review). Mark pin1 and define view on harness drawing. Below numbers are schematic contact numbers, not visual cable order. Power connectors/cables need separate current/temperature qualification. All GPIO/UART/I2C logic is **3.3 V**, no RS-232, no 5 V tolerance assumed.

| Logical connector | Proposed numbered pinout | Voltage/power constraint |
|---|---|---|
| J_PWR_FC, 6 contacts | 1 +5V_FC_IN; 2 +5V_FC_IN; 3 GND; 4 GND; 5 BAT_V_SCALED; 6 BAT_I_SCALED | Regulated FC input only, target 4.9–5.3 V at board; scaled analog protected to 0–3.0 V planning span. No raw battery pin |
| J_GNSS, 6 contacts | 1 switched +5V_GNSS; 2 FC_TX/PA9; 3 FC_RX/PA10; 4 PPS/PA8 optional; 5 reserved NC; 6 GND | 5 V module supply **only if selected GNSS permits it**; power range/current unresolved. Bare 3.3 V GNSS requires redesigned supply/harness |
| J_COMP, 3 contacts | 1 GND; 2 FC_TX/PB9; 3 FC_RX/PB8 | **No 5 V or 3.3 V power contact.** Pi header pin10/GPIO15←FC TX; pin8/GPIO14→FC RX; pin6→GND, subject to OS UART routing validation |
| J_RC, 4 contacts | 1 receiver supply TBD; 2 FC_RX/PB12; 3 FC_TX/PB13; 4 GND | Receiver-specific supply/level/inversion; never bridge TX/RX by default |
| J_TELEM1, 6 contacts | 1 switched +5V_RADIO; 2 FC_TX/PD5; 3 FC_RX/PD6; 4 NC; 5 NC; 6 GND | No hardware flow control; radio peak load and logic pending |
| J_TELEM2 optional, 4 contacts | 1 GND; 2 FC_TX/PD8; 3 FC_RX/PD9; 4 NC | DNP; externally powered accessory |
| J_ESC, 8 contacts | 1 GND; 2 MOTOR1; 3 MOTOR2; 4 MOTOR3; 5 MOTOR4; 6 UART7_RX optional; 7 NC; 8 NC | **No raw battery or motor supply.** Custom harness, NOT plug-compatible with imported J6 or arbitrary 4-in-1 ESC |
| J_DBG, 10-contact keyed 2×5 SWD-style | 1 VTref(3V3); 2 SWDIO; 3 GND; 4 SWCLK; 5 GND; 6 SWO optional; 7 NC/key; 8 NC; 9 GND; 10 NRST | VTref is reference, not probe-powered rail; verify standard/probe mapping |
| J_CONSOLE, 3 contacts | 1 GND; 2 FC_TX/PC6; 3 FC_RX/PC7 | 3.3 V USB-UART adapter; no 5 V adapter power |
| J_BUZZ, 2 contacts | 1 protected buzzer supply; 2 low-side switched return | Passive sounder voltage/current not selected; flyback/clamp if inductive sounder |
| J_CAN optional, 4 contacts | 1 protected +5V optional; 2 CAN_H; 3 CAN_L; 4 GND | DNP; transceiver bus pins, NOT MCU logic pins; switchable 120Ω termination at bus end only |
| J_I2C optional, 4 contacts | 1 protected 3V3; 2 SCL/PD12; 3 SDA/PD13; 4 GND | Short external cable, pull-up/capacitance budget; switch/isolate faults from core |
| USB-C | USB2.0 D+/D−, GND, protected VBUS sense/input, independent CC pulldowns | FS device/service power only; reverse-current isolation; not Pi power or camera USB |

### Motor / receiver electrical release gates

Select PWM or DShot only after ESC documentation. Recommend DShot-capable quad ESC for future diagnostics, but do not promise bidirectional DShot. The four direct logical MCU paths require series damping/ESD and a reviewed idle pulldown or qualified power-off-safe buffer. Do not use a unidirectional buffer if bidirectional DShot becomes mandatory. Verify ESC VIH/VIL, input pull state, cable length, reset/boot waveforms and absence of false pulses. Analog current sense belongs on J_PWR, not unprotected ESC telemetry pin.

UART7 single-wire telemetry sharing is allowed **only** if actual ESC protocol/electrical topology explicitly supports shared wiring. Four independent push-pull telemetry transmitters cannot simply be tied together. RC baseline is a full-duplex electrical interface capable of later CRSF/SBUS configuration; no receiver protocol is committed. SBUS native inversion must be verified end-to-end in the selected PX4 RC driver.

## 3. Companion and camera integration contract

MAVLink2 UART4, 8N1, initial **921600 baud** (verified NXT UART4 buffer/baud precedent, not guaranteed cable performance), no flow-control wire. At 10 wire bits/byte, theoretical payload ceiling before MAVLink framing is 92,160 byte/s; cap planned aggregate sustained traffic to ≤50% initially and measure drops. Fall back to 460800 if signal/CPU testing requires. No debug console or uXRCE-DDS on same UART concurrently.

Use matched 3.3 V logic and short TX/RX-with-ground wiring, away from ESC phases and camera USB. Require power-off I/O-safe buffering/isolation or a demonstrated injection-current-safe design; series resistance alone is not proof against back-powering. Pi5 UART device name/overlay must be verified on selected OS; do not assume the Pi4 `ttyAMA0` tutorial maps to GPIO14/15. Disable serial login on chosen hardware UART, confirm loopback, then connect FC.

Pi USB3 port→short retained USB3 cable→OAK-D Lite; no camera signals reach FC. Example uncompressed streams: 1280×720×3×30 = **82.94 MB/s** RGB plus 640×480×2×30 = **18.43 MB/s** depth, total **101.38 MB/s** before protocol overhead/extra streams. This exceeds USB2 nominal 480 Mbit/s (60 MB/s before overhead); use Pi USB3, encoder/reduced FPS if necessary, and measure actual negotiated speed/drops. These are **example stream choices**, not promised camera modes/performance. OAK onboard processing can reduce Pi/USB load; Pi vision CPU must not delay FC stabilization.

FC arming requires valid configured sensors/estimator/RC or deliberately authorized offboard policy. Pi MAVLink heartbeat is not proof of a healthy command stream; validate PX4 offboard liveness/timeouts and mission-appropriate loss action. Never silently resume armed offboard authority after Pi reboot. Exact failsafe action depends on aircraft and heading/position availability and remains a commissioning decision.
