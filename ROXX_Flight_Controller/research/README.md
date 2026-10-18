# Read-only upstream research snapshots

Fetched 2026-10-18 with GitHub API. These are evidence, **not implemented ROXX firmware**.

* `px4-v1.17.0/`: original relative paths from PX4/PX4-Autopilot, commit `d6f12ad1c4f70ad3230afd7d86e971421e02fef4` (release v1.17.0). Board files and selected barometer driver files. Binary bootloader not copied.
* `px4-main/`: selected comparison files at `ddcaad6601be20453ec6acd0f08e567af3a7e1bb`. Flattened `src/` and `init/` names; paths identified in source registry.
* `st/STM32H743VITx.xml`: STMicroelectronics/STM32_open_pin_data at `7d1f1514ed5583ec5007ad91236b4e1d377295b1`, path `mcu/STM32H743VITx.xml`. Contains vendor pin numbers and permitted functions, not AF numbers or a full electrical specification.

PX4 and ST snapshots retain copyright headers and accompanying BSD-3-Clause notices. See `PX4_LICENSE.txt` and `st/LICENSE.txt`. Do not redistribute restricted SPL06 PDFs or unlicensed third-party CAD assets. No manufacturer datasheet PDFs have been vendored. `snapshot_manifest.csv` records hashes. References and access limitations: `../sources.md`.
