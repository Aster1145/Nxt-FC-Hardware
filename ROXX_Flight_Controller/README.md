# ROXX Flight Controller

**Status: partial — Stage 2 preliminary engineering package. Not approved for fabrication, not flight-ready.**

The decision is final: a **new custom ROXX PX4 flight controller**, Pi 5 companion, USB OAK-D Lite, external GNSS and four ESC-driven BLDC motors. Stabilization/sensors/motor outputs/essential failsafes remain on FC. Original NXT hardware is reference only and remains untouched in `../NxtFC-DUAL` / `../NXTVersion2.0`.

## Review order

1. [architecture.md](architecture.md) — recommended core/sensors, system diagram, corrected upstream support findings and circuit audit.
2. [architecture_decision_matrix.md](architecture_decision_matrix.md) — alternatives, Rev A scope and genuine approval gates.
3. [interface_specification.md](interface_specification.md) and [pin_allocation.csv](pin_allocation.csv) — subsystem map, all 100 MCU package contacts, connector contracts, timer/EXTI/DMA conflicts.
4. [power_tree.md](power_tree.md) — domain diagram, verified loads, explicitly assumed sizing scenarios, unresolved battery envelope and Pi/OAK USB/PD/thermal/transient work.
5. [firmware_integration.md](firmware_integration.md) — verified official NXT target vs proposed ROXX BSP; build/recovery and test boundaries.
6. [preliminary_bom.csv](preliminary_bom.csv), [sources.md](sources.md), [licensing_review.md](licensing_review.md).

The proposed ROXX `roxx_fc-v1` target does **not** exist yet. Research snapshots are read-only evidence, not implemented firmware. Do not flash another board's image onto ROXX hardware.

## Open / reproduce

No ROXX KiCad project has been created before architecture/pin review. To inspect original files, use a disposable copy of `../NxtFC-DUAL/NxtPX4.kicad_pro` in compatible KiCad (export identifies 7.0.9). Library tables are missing; see audit. Do not allow automatic saves/migration of imported originals.

From repository root:

```sh
# Standard-library pin allocation check/generation:
python ROXX_Flight_Controller/tools/generate_pin_allocation.py
# Reference extraction requires a venv with versions in audit/tool_versions.txt:
python ROXX_Flight_Controller/tools/audit_reference.py
```

The reference extractor reads original tracked files and writes only `audit/`. CSVs are structural evidence, not ERC/DRC reports or orderable BOMs. Snapshot provenance is in `research/README.md`, `research/snapshot_manifest.csv` and sources registry. Manufacturer CAD/datasheet viewing is not a redistribution grant.

## Deliverable status

| Deliverable | Status |
|---|---|
| README / change log | Complete through current stage |
| requirements.md | Partial; final product boundary recorded, detailed specifications pending |
| architecture.md / architecture_decision_matrix.md | Partial; recommendation complete for review, component/critical pin approval pending |
| hardware_audit.md | Partial; structural inspection complete plus Stage 2 corrections, electrical/footprint tests pending |
| interface_specification.md / pin_allocation.csv | Partial; preliminary allocations complete, AF/DMA/protocol/connector freeze pending |
| power_tree.md | Partial; equations and scenario budgets complete, actual source/load/thermal qualification blocked |
| firmware_integration.md | Partial; upstream source/asset existence verified, ROXX implementation/build/physical tests not done |
| validation_plan.md | Partial; staged tests and actual ledger, physical validation not started |
| preliminary_bom.csv | Partial; candidate functional BOM, not assembly/order BOM; missing passives/protection/connector MPNs explicit |
| licensing_review.md / sources.md | Partial rights verification / complete current research registry with access limitations |
| ROXX KiCad schematic/PCB/project | Blocked pending architecture and critical-pin review; no routing begun |
| Manufacturing BOM / fabrication / assembly files | Blocked pending approved schematic/layout and validation |
| Project libraries / optional STEP models | Blocked pending selected parts, footprint verification and individual licenses |

No KiCad CLI was found in Stage 1; ERC/DRC have not been run. No reference or ROXX firmware builds, electrical simulations, lab tests or flights have been performed. Source-target existence and pin CSV validation are not a safety signoff.
