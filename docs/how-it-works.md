# How it works — technical walkthrough

For BIM managers, developers, and estimators who want to understand what's actually happening.

## The pipeline

```
┌──────────────┐   MCP    ┌───────────────┐   JSON    ┌──────────────┐   .xlsx
│  Revit model │ ───────▶ │  score_model  │ ────────▶ │build_scorecard│ ────────▶  deliverable
│  (open in    │          │  IronPython   │           │  Python +    │
│   Revit)     │          │  runs INSIDE  │           │  openpyxl    │
└──────────────┘          │    Revit      │           └──────────────┘
                          └───────┬───────┘
                                  │  autofix (optional)
                                  ▼
                          writes Assembly Codes
                          back into the model
```

- **`score_model.py`** runs inside Revit's process (via pyRevit + the Revit MCP + IronPython 2.7). It has direct access to `doc`, the Revit API, and every element.
- **`build_scorecard.py`** runs in host Python (3.x). It reads the JSON dumped by the engine and builds a formatted `.xlsx` with openpyxl. No Revit connection needed for this step — it's pure Python.
- **`autofix_assembly_code.py`** runs inside Revit (same way as the engine) and writes back to element types.

Split like this because IronPython 2.7 has no openpyxl, and CPython can't touch Revit. The JSON handoff keeps the two clean.

## The scoring math

Every rule produces a `passrate` in [0.0, 1.0] and carries a `severity` in `{fail, warn, info}` and a `weight` (integer, usually 1–3).

```
SEV_FACTOR = {fail: 1.0, warn: 0.5, info: 0.0}

category_score = 100 × Σ(weight × sev_factor × passrate)
                     ─────────────────────────────────
                        Σ(weight × sev_factor)

overall = weighted mean of category_scores, using CAT_WEIGHTS
```

`CAT_WEIGHTS = {naming: 0.15, parameters: 0.35, classification: 0.20, geometry: 0.20, worksharing: 0.10}`.

Info rules (advisory / `na_allowed`) are shown in the report but excluded from scoring — they can't drag the grade down.

## Category-aware classification

The single most important design decision, learned by testing on real models:

| Family kind | Classification | Auto-fixable? |
|---|---|---|
| **Loadable** (Doors, Windows, MEP fixtures, Furniture, Casework, Structural Framing/Columns, Footings) | OmniClass Number + Assembly Code | Only Assembly Code |
| **System** (Walls, Floors, Roofs, Ceilings, Foundation Slabs) | Assembly Code only (no OmniClass parameter) | Assembly Code |

A naive "every element must have OmniClass" rule would false-flag every wall in every model. The engine splits by family kind and applies the right rule per element.

## Stage-based severity

Some parameters are *required* at some stages and *optional* at others:

| Parameter | Design (SD/DD) | Fabrication | Operations |
|---|---|---|---|
| Structural Type Mark | advisory (info) | required (fail) | required (fail) |
| MEP Manufacturer/Model | advisory (info) | advisory | required (fail) |
| Door Fire Rating (universal) | `na_allowed` — always advisory | `na_allowed` | `na_allowed` |

Set `STAGE = "design"` / `"fabrication"` / `"operations"` at the top of `score_model.py`. Rules with `severity_by_stage: {design: info, fabrication: fail, ...}` resolve to the right severity for the run. A client's BEP can override any rule's stage table.

## `na_allowed` — the "blank is OK" escape hatch

A blank Fire Rating on a non-fire-rated door isn't a defect — it's correct. The rulebook has a `na_allowed: true` flag: those rules produce a coverage percentage (info) but never a failure. Same for design-stage Type Marks. This matches the LOD spec's own language — it never lists Fire Rating as a universal requirement.

## Verified sources for every rule

Every rule carries a `src` string that lands in the Rule Detail tab of the Excel. That's the credibility layer.

- `LOD B1010` → BIMForum LOD Spec 2024, Steel Framing Column section
- `LOD C1030` → LOD Spec, Interior Swinging Doors
- `LOD C1020` → LOD Spec, Windows (U-value / operation)
- `LOD/OC21`, `LOD/UF` → classification codes cross-referenced in the LOD spec (rules/tables/classification_map.md)
- `COBie Type`, `COBie Space` → COBie-US 2.4 template columns (rules/tables/cobie_columns.md)
- `ISO 19650` → UK profile naming (rules.uk.yaml)
- `practitioner` → thresholds that no standard fixes (warnings count, in-place family caps) — client-tunable

See [VERIFICATION.md](../VERIFICATION.md) for the full three-tier ledger.

## The auto-fix mechanism

`autofix_assembly_code.py`:

1. For each category (Doors, Windows, MEP fixtures, Furniture, Casework, Structural Framing/Columns/Foundations), collects the element TYPES.
2. Computes each category's **modal existing Assembly Code** (the most-common non-blank value).
3. If a type has a blank Assembly Code, fills it with the modal (or a Uniformat Level-3 default if the whole category is blank).
4. Never overwrites an existing value.

The MCP auto-commits — writes persist immediately. Ctrl+Z in Revit reverts them.

Real result on Snowdon Structural: 8 blank type definitions filled (Framing → B10, Columns → B10, Foundations → A1010100), classification score lifted, overall grade nudged up.

## The MCP transaction constraint

`mcp__revit__execute_revit_code` wraps every call in its own Revit transaction and commits before returning. Consequences:

- **No nested transactions.** Any code that tries `Transaction.Start()` fails.
- **No in-call rollback.** Writes persist immediately. Ctrl+Z is your only undo.
- **`doc.EditFamily()` won't work.** It requires the document *not* be modifiable. That's why OmniClass can't be auto-fixed through this MCP — the family-editor route is blocked.
- **A big script that errors partway through still persists writes made before the error.** Keep remediation scripts small.

## Design decisions worth knowing

- **Parameters weighted heaviest (0.35).** This is what downstream tools (QTO, cost, FM handover) consume. Bad classification is bad; bad parameters break the whole downstream flow.
- **Grades map to `{A: 90, B: 80, C: 70, D: 60, F: <60}`.** School-style so clients understand instantly. Not gospel — override in `rules.custom.yaml`.
- **Assembly Code (Uniformat) is the classification auto-fix target, not OmniClass.** It's writable via the API, per-type, fast, reversible, and it's what US estimators actually price from. OmniClass is a nice-to-have; Uniformat is what pays the bills.
- **Worksharing on standalone files = info, not failure.** A sample or single-user file shouldn't drop a full letter grade for being non-workshared.
