---
name: bim-health-scorecard
description: Audit a live Revit model for data-quality issues (missing parameters, wrong naming, bad/missing classifications, geometry hygiene, worksharing), grade it A–F, produce a color-coded Excel scorecard with clickable failing-element IDs, and optionally auto-fix safe issues back into the model. Use when the user asks to score/audit/grade a Revit model, run a BIM health check, generate a scorecard, find missing OmniClass/Assembly Codes, or fix Uniformat classification. Requires AutoConst Revit MCP + the model open in Revit.
---

# BIM Health Scorecard

Audits the Revit model currently open in Revit using the native AutoConst Revit MCP tools
`bim_health_audit` and `bim_health_fix` (scorecard engine v1.3, ported and parity-tested),
writes a formatted `.xlsx`, and can fill blank Uniformat (Assembly Code) codes back into the model.

## Prerequisites
1. Revit is running with a project open; pyRevit Routes on `localhost:48884`.
2. AutoConst Revit MCP is connected (`mcp__revit__bim_health_audit` / `mcp__revit__bim_health_fix` available).
   If those tools are missing, the MCP is an older version: tell the user, don't fall back silently.
3. The scorecard repo is cloned: `C:\Users\Hamza\autoconst-claude-bim-health-scorecard`
   (else Glob for `autoconst-claude-bim-health-scorecard` under the user's home).
4. Host Python + openpyxl (`py -m pip install openpyxl` if missing).

## A) Score the open model → Excel scorecard
1. Call `mcp__revit__bim_health_audit` with `stage` ("design" unless the user says fabrication/operations)
   and `max_failing_ids: 5` — this is for the chat summary only; keep it small.
   Its result is ONE JSON document: read `overall`, `grade`, `category_scores`, and the rules with
   the lowest `pass_rate` / highest `fail_count` (skip `applicable: false` and `advisory: true` rules).
2. Build the workbook (the builder fetches the complete, uncapped audit itself — no tokens):
   `py <repo>/engine/build_scorecard.py --fetch --stage <stage>`
   It saves `<repo>/outputs/scorecard_data.json` and writes
   `<repo>/outputs/BIM-Health-Scorecard-<model>.xlsx`. Its last line reports grade and whether the
   Failing Elements sheet is `(complete)` or `(SAMPLE - capped)`. If it says SAMPLE, tell the user.
3. `SendUserFile` the `.xlsx`; caption = grade + score + the 2–3 biggest problems.

## B) Fill blank Uniformat Assembly Codes (writes to the model — two steps)
1. Preview: `mcp__revit__bim_health_fix` with no arguments. Nothing is written.
2. Show the user `summary.categories` (category → fill value, blank type count) and flag doubtful
   fills: the v1.3 policy gives EVERY blank type in a category that category's most common code
   (e.g. faucets and floor grates get the water-closet code D2010110). Ask before applying.
3. On a clear yes: `mcp__revit__bim_health_fix` with `apply: true` and the preview's `plan_id`.
   - `transaction.status: committed` → done; one Ctrl+Z in Revit ("AutoConst: fill Assembly Codes") undoes it.
   - `error_code: stale_plan` → the model changed; show the fresh preview, ask again.
   - Timeout / unknown → do NOT re-apply. Run the preview again to see the real state.
4. Re-run mode A and show the before/after grade.
Scope: Structural Framing/Columns/Foundations, Windows, Plumbing & Lighting Fixtures, Casework,
Furniture. Doors and system families (walls/floors/roofs/ceilings, rule C-05) are NOT fixed.

## C) Color-splash failing elements in Revit (visual demo)
1. Run mode A first (`outputs/scorecard_data.json` must exist).
2. Read `engine/color_splash_failures.py` (leave `CLEAR = False`) and send via `mcp__revit__execute_revit_code`.
3. Red = fail, orange = warn, yellow = advisory, in the active view. Re-run with `CLEAR = True` to reset.

## D) Stages
- `design` (default): asset data (Manufacturer/Model) and structural Type Mark are advisory.
- `fabrication`: asset-data rules become `warn`.
- `operations`: asset-data rules become `fail`.
- Known v1.3 quirk (kept for parity): P-09m structural Type Mark stays advisory at every stage.
- UK/Uniclass profile is not in the native tool yet — say so if asked.

## Conventions (verified live — do not re-litigate)
- `OmniClass Number` is read-only via the API; only `Assembly Code` (Uniformat) can be filled.
- `doc.EditFamily()` fails inside the MCP ("document is currently modifiable") — no family-editor fixes.
- System families (Walls/Floors/Roofs/Ceilings) carry Assembly Code only, never OmniClass.
- Treat `None` and `""` as empty. Type-level vs instance-level parameters are handled by the engine.
- Scoring: SEV_FACTOR fail 1.0 / warn 0.5 / info 0; category = weighted pass rate; overall = weighted
  mean over categories that have scoring rules; A≥90 B≥80 C≥70 D≥60 F<60.
- Snowdon Towers Sample Architectural reference scores (unfixed): design 85.15 B, fabrication 80.41 B,
  operations 76.78 C. After mode B: design 85.77 B.

## Source-citation policy
Every rule carries a `source` (LOD <code>, LOD/OC21, LOD/Uniformat, COBie Type/Space, practitioner),
shown on the Rule Detail tab. Only claim "per standard X" for LOD/COBie-sourced rules.

## When something goes wrong
- Tool returns `status: error` with "No active Revit document" → ask the user to open a project.
- Builder says "Cannot reach Revit" → Revit/pyRevit Routes not running.
- Builder exits "Failing-element list incomplete" → do not send a workbook; report it.
- openpyxl missing → `py -m pip install openpyxl`, retry.
