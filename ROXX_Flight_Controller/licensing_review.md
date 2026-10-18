# Licensing / asset release gate — Stage 2

**Status: partial — known notices identified; third-party CAD redistribution not cleared.** No original CAD/models copied into a new ROXX design. Original reference files remain unchanged.

| Asset | Established license/evidence | Action |
|---|---|---|
| Imported repository source | Root BSD-3-Clause, 2023 Peize-Liu | Retain root notice and attribution for derived circuits/layout; do not imply endorsement |
| PX4 board/driver snapshots in research | BSD-3-Clause headers and `research/PX4_LICENSE.txt` | Keep all notices; record source SHA; separate snapshots from implemented ROXX firmware |
| ST pin XML and derived pin mapping | ST open pin data repository BSD-3-Clause; `research/st/LICENSE.txt` | Retain copyright/license for XML and derived allocations; don't interpret as electrical certification |
| Actual future PX4/NuttX firmware | PX4 license does not automatically cover every submodule | Audit NuttX, libraries and bootloader notices at pinned SHAs when firmware is built/distributed |
| Imported custom BMI088/MCU/regulator symbols and footprints | Root repository license exists; per-item provenance is undocumented | Rebuild/audit from manufacturer drawings or establish provenance; do not claim third-party ownership is proven by root notice |
| Imported connector custom footprints | Exact connector manufacturer/MPN and source rights unknown | Prefer audited manufacturer drawing + original ROXX footprint, or licensed KiCad official symbol/footprint with proper notice/version |
| Official KiCad library assets | Not vendored or version-audited yet | Verify chosen library license (commonly CC-BY-SA with KiCad exception) and version; retain required attribution; do not apply assumed terms to all assets |
| Imported STEP models | Many appear vendor-derived; individual redistribution grants absent | Quarantine from new package until item-specific license recorded, or omit/replace with licensed model; 3D is optional, not an electrical requirement |
| SPL06 PDF linked in source | Third-party-hosted manufacturer document explicitly marked Restricted | Do not vendor, copy into release or claim redistribution rights. Request public authoritative documentation if SPL06 reconsidered |
| STM/Bosch/TI datasheets | Public viewing does not grant unrestricted redistribution | Link to official resources; create original circuit/footprint from dimensional/electrical facts; do not bundle PDFs without permission |
| Nxt/HKU/HILAB/author artwork and signatures | No separate trademark/logo authorization established | Do not carry into ROXX branding or use as endorsement |

New design asset manifest must list each symbol/footprint/model's source URL, revision/hash, author, license/exception, local modifications and redistribution disposition. No manufacturing release until required electrical footprints are checked and redistributable. Optional STEP models can be omitted without blocking an electrically complete release.
