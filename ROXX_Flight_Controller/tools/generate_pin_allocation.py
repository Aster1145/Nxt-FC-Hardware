"""Generate preliminary 100-contact map from pinned ST XML. Not a KiCad netlist.
Checks unique package contact/GPIO assignment and vendor function membership.
Does NOT check NuttX AF macros, electrical levels, DMA, schematic connectivity.
Run from any directory with Python standard library.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import csv
root=Path(__file__).resolve().parents[1]
ns={'m':'http://dummy.com'}
xml=ET.parse(root/'research/st/STM32H743VITx.xml').getroot()
# gpio, net/role, vendor function, implementation status
spec='''PA5|IMU1_SCK|SPI1_SCK|mandatory
PA6|IMU1_MISO|SPI1_MISO|mandatory
PA7|IMU1_MOSI|SPI1_MOSI|mandatory
PA3|IMU1_GCS_N|GPIO|mandatory
PA2|IMU1_ACS_N|GPIO|mandatory
PA1|IMU1_GDRDY_EXTI1|GPIO|mandatory
PA0|IMU1_ADRDY_EXTI0|GPIO|mandatory
PE2|IMU2_SCK|SPI4_SCK|mandatory
PE5|IMU2_MISO|SPI4_MISO|mandatory
PE6|IMU2_MOSI|SPI4_MOSI|mandatory
PC0|IMU2_GCS_N|GPIO|mandatory-new-CS
PC13|IMU2_ACS_N|GPIO|mandatory
PE3|IMU2_GDRDY_EXTI3|GPIO|mandatory
PE4|IMU2_ADRDY_EXTI4|GPIO|mandatory
PD4|IMU1_LDO_EN|GPIO|mandatory-new
PD10|IMU2_LDO_EN|GPIO|mandatory-new
PB6|BARO_SCL|I2C1_SCL|mandatory
PB7|BARO_SDA|I2C1_SDA|mandatory
PA9|GNSS_TX|USART1_TX|mandatory
PA10|GNSS_RX|USART1_RX|mandatory
PA8|GNSS_PPS_EXTI8|GPIO|optional-reserve-not-capture-timer
PB9|COMPANION_TX|UART4_TX|mandatory
PB8|COMPANION_RX|UART4_RX|mandatory
PB13|RC_TX|UART5_TX|mandatory
PB12|RC_RX|UART5_RX|mandatory
PD5|TELEM1_TX|USART2_TX|mandatory
PD6|TELEM1_RX|USART2_RX|mandatory
PD8|TELEM2_TX|USART3_TX|optional-reserve
PD9|TELEM2_RX|USART3_RX|optional-reserve
PE7|ESC_TELEM_RX|UART7_RX|optional-reserve
PE8|ESC_TELEM_TX|UART7_TX|optional-reserve
PC6|CONSOLE_TX|USART6_TX|mandatory
PC7|CONSOLE_RX|USART6_RX|mandatory
PA11|USB_DM|USB_OTG_FS_DM|mandatory
PA12|USB_DP|USB_OTG_FS_DP|mandatory
PD7|USB_VBUS_SENSE_PROTECTED|GPIO|mandatory-relocated
PA13|SWDIO|DEBUG_JTMS-SWDIO|mandatory
PA14|SWCLK|DEBUG_JTCK-SWCLK|mandatory
PB3|SWO|DEBUG_JTDO-SWO|optional-testpoint
PE9|MOTOR1|TIM1_CH1|mandatory
PE11|MOTOR2|TIM1_CH2|mandatory
PE13|MOTOR3|TIM1_CH3|mandatory
PE14|MOTOR4|TIM1_CH4|mandatory
PD14|BUZZER_PWM|TIM4_CH3|mandatory-new
PC4|BAT_V_SCALED|ADC1_INP4|mandatory
PC5|BAT_I_SCALED|ADC1_INP8|mandatory
PC8|SD_D0|SDMMC1_D0|mandatory
PC9|SD_D1|SDMMC1_D1|mandatory
PC10|SD_D2|SDMMC1_D2|mandatory
PC11|SD_D3|SDMMC1_D3|mandatory
PC12|SD_CK|SDMMC1_CK|mandatory
PD2|SD_CMD|SDMMC1_CMD|mandatory
PD15|LED_RED_N|GPIO|mandatory
PD11|LED_GREEN_N|GPIO|mandatory
PB15|LED_BLUE_N|GPIO|mandatory
PD0|CAN1_RX|FDCAN1_RX|optional-reserve
PD1|CAN1_TX|FDCAN1_TX|optional-reserve
PD12|EXT_I2C_SCL|I2C4_SCL|optional-reserve
PD13|EXT_I2C_SDA|I2C4_SDA|optional-reserve
PE10|CORE_PGOOD_INPUT|GPIO|mandatory-new
PH0|HSE_16MHZ_IN|RCC_OSC_IN|mandatory
PH1|HSE_OUT_UNUSED_OSCILLATOR_MODE|GPIO|reserved-no-connect
PC14|LSE_IN|RCC_OSC32_IN|optional-DNP
PC15|LSE_OUT|RCC_OSC32_OUT|optional-DNP'''
roles={}
for line in spec.splitlines():
 gpio,role,fun,status=line.split('|'); assert gpio not in roles;roles[gpio]=(role,fun,status)
rows=[];used=set()
for p in xml.findall('m:Pin',ns):
 raw=p.attrib['Name']; name=raw.split(' ')[0].split('-')[0]; pos=p.attrib['Position']
 if name in roles:
  role,fun,status=roles[name]; assert fun in [x.attrib['Name'] for x in p.findall('m:Signal',ns)],(name,fun)
  used.add(name)
 elif name in ['VDD','VSS','VSSA','VDDA','VREF+','VBAT','VCAP','NRST','BOOT0']:
  role={'VCAP':'internal-regulator-capacitor-NOT-external-supply','BOOT0':'pulldown-and-recovery-pad','NRST':'reset-supervisor-SWD-and-button','VBAT':'tie-to-3V3-no-battery-revA','VDDA':'filtered-3V3-analog','VREF+':'filtered-3V3-reference'}.get(name,name)
  fun='power/reset';status='mandatory-datasheet-audit'
 else: role='UNASSIGNED-no-external-drive';fun='GPIO';status='reserved'
 rows.append([int(pos),raw,role,fun,status])
assert used==set(roles),set(roles)-used
assert len(rows)==100 and len({r[0] for r in rows})==100
with (root/'pin_allocation.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['LQFP100_contact','MCU_signal','ROXX_net_or_role','vendor_function','status']);w.writerows(sorted(rows))
print(f'PASS: {len(rows)} unique package contacts; {len(roles)} unique assigned GPIOs, all functions in pinned ST XML. Not AF/DMA/electrical validation.')
