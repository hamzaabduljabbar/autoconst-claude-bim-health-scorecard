---
name: bim-health-scorecard
description: Audit a live Revit model for data-quality issues (missing parameters, wrong naming, bad/missing classifications, geometry hygiene, worksharing), grade it A–F, produce a color-coded Excel scorecard with clickable failing-element IDs, and optionally auto-fix safe issues back into the model. Use when the user asks to score/audit/grade a Revit model, run a BIM health check, generate a scorecard, find missing OmniClass/Assembly Codes, or fix Uniformat classification. Requires Revit MCP + the model open in Revit.
---

# BIM Health Scorecard

Audits the Revit model currently open in Revit, scores it across five weighted categories, writes a formatted `.xlsx`, and can fill blank Uniformat (Assembly Code) codes back into the model.

## Prerequisites (must be true or the skill fails)
1. Revit is running with a project open.
2. pyRevit + Routes server is running on `localhost:48884`.
3. The Revit MCP is registered with Claude Code (`mcp__revit__*` tools available).
4. This repo is cloned locally (find it via `Glob` for `autoconst-claude-bim-health-scorecard` under the user's home). Fall back to `C:\Users\Hamza\Downloads\bim-health-scorecard` if the repo isn't cloned yet.
5. Host-side Python + openpyxl is installed (`py -m pip install openpyxl` if not).

## Flow — three modes

### A) Score the open model → produce the Excel scorecard
1. Confirm the MCP is up: call `mcp__revit__get_revit_status`. Bail with a clear message if not.
2. Read `engine/score_model.py`. Send the whole script via `mcp__revit__execute_revit_code`, **except** replace the final `print(...)` block with a `json.dumps(...)` write to `<repo>/outputs/scorecard_data.json`. Use `STAGE = "design"` unless the user specified otherwise.
3. In Bash, run: `py <repo>/engine/build_scorecard.py`. It reads the JSON and writes `<repo>/outputs/BIM-Health-Scorecard-<model>.xlsx`.
4. `SendUserFile` the `.xlsx` with a one-line caption: overall grade + score.

### B) Auto-fix blank Uniformat Assembly Codes
1. Read `engine/autofix_assembly_code.py`. Set `APPLY = True`. Send via `execute_revit_code`.
2. It fills blank `Assembly Code` on element TYPES only, deriving fill value from each category's own most-common existing code (fallback to Uniformat Level-3 default). Never overwrites existing values.
3. Re-run mode A. Show the user the before/after grade delta.

### C) Color-splash failing elements in Revit (the visual demo)
1. Make sure mode A has run (JSON exists at `<repo>/outputs/scorecard_data.json`).
2. Read `engine/color_splash_failures.py` (leave `CLEAR = False`). Send via `execute_revit_code`.
3. It paints failing elements in the active view: **red** = fail, **orange** = warn, **yellow** = info/advisory. User can rotate/pan/zoom in Revit to see the problems visually.
4. To wipe the overrides, run the same script with `CLEAR = True`.

### D) Stage / profile switching
- Fabrication stage: set `STAGE = "fabrication"` before running mode A. Structural Type Marks then count against the grade.
- Operations stage: `STAGE = "operations"`. MEP Manufacturer/Model becomes required.
- UK profile: swap to `rules/rules.uk.yaml` semantics (ISO 19650 naming, Uniclass 2015). The UK rulebook is descriptive; the engine's category-aware Classification logic still applies — swap `OmniClass Number` checks for `Classification.Uniclass.Ss.Number` / `Pr.Number`.

## Engine conventions (VERIFIED live — do not re-litigate)
- **MCP transaction**: `execute_revit_code` auto-wraps every call in a Revit transaction and commits it. No in-call rollback; writes persist. Ctrl+Z reverts.
- **`OmniClass Number` is read-only** via `LookupParameter().Set()`. Never try to auto-fix it here. `Assembly Code` (Uniformat) IS writable — use that.
- **`doc.EditFamily()` FAILS inside the MCP** with "The document is currently modifiable!". Family-editor OmniClass fix is impossible through this MCP. Deliver as pyRevit tool if ever needed.
- **Terse MCP read tools** (`list_category_parameters`, `ai_element_filter`, `get_current_view_elements`) return only summary strings. Always use `execute_revit_code` for structured data.
- **Category-aware classification**: loadable families (Doors, Windows, MEP fixtures, Furniture, Casework, Structural Framing/Columns) carry OmniClass. System families (Walls, Floors, Roofs, Ceilings) carry Assembly Code (Uniformat) — never OmniClass. Foundations split by `isinstance(e, FamilyInstance)`: footings (loadable) vs slabs (system).
- **Empty values**: treat `None` AND `""` as empty. Revit returns `""` for cleared text params (e.g. Room Occupancy).
- **Parameter scope**: type-level params — OmniClass Number, Assembly Code, Type Mark, Fire Rating, Width, Height, Function, Manufacturer, Model, Description. Instance-level — Mark, Occupancy, Department, Structural, Name, Number, Area.
- **CAD imports**: filter `ImportInstance` where `IsLinked == False` (the raw collector returns links + imports together).
- **N/A allowed**: `Fire Rating` on non-fire-rated doors and `Type Mark` on structural members at design stage are `na_allowed: true` — blank never fails, only counted as advisory coverage. This matches the LOD spec (LOD never lists Fire Rating as universal).

## Scoring math
- `SEV_FACTOR = {"fail": 1.0, "warn": 0.5, "info": 0.0}` — info rules are excluded from the score, only shown in the report.
- Category score = `100 * sum(weight * sev_factor * passrate) / sum(weight * sev_factor)`
- Overall = weighted mean of category scores.
- Grade bands: A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, F < 60.

## Source-citation policy
Every rule carries a `src` string used in the Rule Detail tab. Prefixes:
- `LOD <code>` — BIMForum LOD Spec 2024 element section (Tier 1)
- `LOD/OC21`, `LOD/UF` — classification codes cross-referenced from the LOD spec
- `COBie Type`, `COBie Space` — COBie-US 2.4 sheet (Tier 1 column names)
- `ISO 19650` — UK profile naming/status codes (Tier 2, blog-sourced regex)
- `practitioner` — rule-of-thumb thresholds (Tier 3, client-tunable)

## When something goes wrong
- `execute_revit_code` returns an empty `Error:` string → transient; call `mcp__revit__get_revit_status` to confirm alive, then retry once with a smaller script. Split into chunks if it keeps failing on a large script.
- User opened a different model between calls → re-check `get_revit_status` before scoring.
- Openpyxl not installed → run `py -m pip install openpyxl` and retry.
