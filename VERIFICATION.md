# Verification status — what's proven vs sourced vs chosen

Honest ledger of how much we can defend each part of the scorecard. Keep this
current. When talking to a client, only claim "per standard X" for Tier 1/2.

## Tier 1 — VERIFIED against real Revit models
Tested directly on Snowdon Towers Architectural + Structural via the Revit MCP.
- Parameter names exist and resolve: OmniClass Number, Assembly Code, Type Mark,
  Fire Rating, Function, Structural Material, Mark, Occupancy, Department, etc.
- `OmniClass Number` is READ-ONLY via param write; `Assembly Code` is WRITABLE.
- OmniClass codes are dot-separated (e.g. 23.30.10.00 / 23.25.30.11.14.14).
- Type-vs-instance parameter scope per param (documented in rules conventions).
- System families (Walls/Floors/Roofs) carry NO OmniClass — Assembly Code only.
- Scoring math, category rollup, letter grade, and the write-back auto-fix all
  run correctly on 17k- and ~1k-element models across two disciplines.
- MCP endpoint auto-commits each call (no in-call rollback; Ctrl+Z reverts).

## PRIMARY-SOURCE READ LOG (2026-07-30)
- BIMForum LOD Spec 2024 Part I: READ locally (4.6MB PDF, page-by-page).
  RESULT: Part I is ELEMENT GEOMETRY only — LOD 100–400 "Inclusions" describe
  what geometry to model, NOT which data fields must be filled. It does NOT
  contain the required-parameter matrix. HOWEVER it authoritatively lists the
  Uniformat/OmniClass/Uniclass/MasterFormat code per element -> transcribed to
  rules/tables/classification_map.md (now Tier 1, see below).
  The required-ATTRIBUTE matrices are in LOD Spec PART II (Data Tables), a
  separate PDF — still needed.
- COBie mandatory-column matrix: NOT obtained. Web sources confirm the color
  rule (yellow = mandatory, enter "n/a" if unknown) but no per-sheet column
  list. Needs NBIMS-US v3 §4.2 or the actual COBie spreadsheet template.

## PRIMARY-SOURCE READ LOG — UPDATE 2 (2026-07-30)
- BIMForum.Global 2024 LOD Spec, October 2024 COMBINED edition: downloaded
  (9.7MB) and read locally. This edition DOES include a "Non-graphic
  information associated with model element" block per element per LOD — the
  required-attribute source the older Part I lacked. Worked examples (Windows,
  Steel Framing Column) transcribed to rules/tables/lod_data_attributes.md.
  Data richness varies by element; spec defers final data reqs to the BIM PEP.
- COBie-US 2.4 template: downloaded (xBim, 459KB .xls) and parsed with
  Python/xlrd. Full verified column list for all core sheets ->
  rules/tables/cobie_columns.md. Template headers are uniform gray (no yellow
  coding), so mandatory split follows the COBie standard (still Tier 2), but
  column NAMES are Tier 1 verified.

## LOD EXTRACTION COMPLETE (representative set, 2026-07-30)
Transcribed element sections across all major disciplines: Windows, Interior
Doors, Steel Framing, Foundations/Walls, HVAC, Plumbing, Lighting ->
rules/tables/lod_data_attributes.md. Definitive finding: LOD mandates GEOMETRY +
type/material/size (Tier 1) and some performance (windows); it explicitly DEFERS
asset/FM data (Manufacturer, Model, Serial, Cost, Warranty) to the BIM PEP and
COBie. So the scorecard's param rules are now sourced as:
  - size/material/type/operation  -> LOD spec (Tier 1)
  - Manufacturer/Model/Cost/etc.  -> COBie Type/Component sheets (Tier 1 names)
  - Fire Rating                    -> na_allowed (LOD lists it nowhere as
                                      universal; only fire-rated openings) ✓

## Tier 2 — remaining (updated)
- COBie MANDATORY-column split: Tier 2 (standard-defined; template not
  color-coded). Column names are Tier 1.
- ISO 19650 naming regex + status/revision codes: from blogs, not the paywalled
  ISO 19650-2 text.
- OmniClass regex validity check confirms FORMAT only, not table membership
  (no OmniClass 23 Products table loaded yet).

## Tier 1 (promoted) — classification code map
- Uniformat/OmniClass/Uniclass code per element: NOW Tier 1, transcribed from
  the LOD Spec 2024 Part I -> rules/tables/classification_map.md. The Assembly
  Code (Uniformat) auto-fix defaults are standard-backed. (Caveat: Revit's
  "OmniClass Number" on loadable families is OmniClass 23 Products, a different
  table than the OmniClass 21 Elements codes in the map — don't conflate.)

TO PROMOTE REMAINING TIER 2 -> TIER 1: ingest LOD Spec PART II Data Tables and
the NBIMS-US v3 COBie workbook for the required-parameter + mandatory-column
matrices.

## Tier 3 — DESIGN CHOICES (our methodology, not any standard)
Reasonable but they are opinions. These are the FIRST things a client should be
allowed to override in rules.custom.yaml.
- Category weights (naming .15 / parameters .35 / classification .20 /
  geometry .20 / worksharing .10).
- Grade bands (A>=90, B>=80, C>=70, D>=60).
- Numeric thresholds (warnings >100 warn / >1000 fail; file >300MB/>1GB;
  family >1MB/>3MB). Practitioner consensus; NO standard fixes these.
- Severity assignments (which rules are fail vs warn vs info), including the
  stage-based calls below.

## Stage-based severity calls (locked in v1)
Some params are required at fabrication/handover but blank-and-acceptable at
design stage. Default = design-stage profile (advisory); fabrication profile
flips them to fail via rules.custom.yaml.
- Door Fire Rating: advisory (blank OK on non-rated doors).
- Structural Type Mark (framing/columns): ADVISORY by default (design stage),
  overridable to REQUIRED for a fabrication/detailing BEP.
