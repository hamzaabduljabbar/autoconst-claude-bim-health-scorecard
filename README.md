# BIM Health Scorecard

Point it at a **live Revit model**, get back a **color-coded Excel scorecard** with an A–F grade — every failing element listed with its ID so your BIM manager can click straight to the problem in Revit. Then, when you're ready, it auto-fixes the safe stuff (missing Uniformat cost codes) back into the model.

Free, self-hosted, runs on your machine. Every rule cites the standard it came from (BIMForum LOD 2024, COBie, ISO 19650).

> Built by [Hamza Jabbar](https://hamzajabbar.online) · AutoConst

---

## What you get

<p align="center">
  <em>3 tabs per scorecard: Summary (grade + category scores) · Rule Detail (every check with source) · Failing Elements (clickable IDs)</em>
</p>

- **Overall grade A–F** on a 100-point scale, plus a per-category grade (Naming, Parameters, Classification, Geometry, Worksharing).
- **Every failing element listed** by ID — jump to it in Revit with one click (Manage → Select by ID).
- **Every rule sourced** — `LOD C1030`, `COBie Type`, `ISO 19650` etc., right in the Rule Detail tab. No unsourced opinions.
- **Auto-fix for the safe stuff** — fills blank Uniformat *Assembly Code* on element types (the code US estimators price from). Reversible with Ctrl+Z.
- **US + UK profiles** — Uniformat/OmniClass/COBie for US, ISO 19650 + Uniclass 2015 for UK.
- **Stage-aware** — design vs fabrication vs operations flips what's required (structural Type Marks matter for fab, not for SD; MEP Manufacturer/Model matters for handover, not for SD).

Two real example scorecards are in `samples/` — open them to see exactly what the deliverable looks like.

---

## Prerequisites — read this before anything else

You need **five** things installed. The setup takes about 15 minutes end to end; after that, running the scorecard is one command.

| # | What | Why | How |
|---|---|---|---|
| 1 | **Windows 10/11** | Revit is Windows-only | – |
| 2 | **Autodesk Revit 2024/2025/2026** | The model to audit | – |
| 3 | **pyRevit** | Lets scripts run inside Revit | See step-by-step below |
| 4 | **Revit MCP Server** | Bridge between Claude and Revit | See step-by-step below |
| 5 | **Claude Code** | Runs the skill | [claude.com/product/claude-code](https://claude.com/product/claude-code) |

---

## Setup — one-time (~15 min)

### Step 1 — Install pyRevit
pyRevit is a free Revit add-in. The MCP server talks to Revit through it.

1. Go to https://github.com/pyrevitlabs/pyRevit/releases
2. Download the latest **.exe installer** (e.g. `pyRevit_CLI_x.x.x.x_admin_signed.exe`)
3. Run the installer — accept defaults
4. Open (or restart) Revit — you should see a **pyRevit** tab in the ribbon
5. In the pyRevit tab: **Settings** (gear icon) → **Routes** section → check **Enable Routes Server** → **Save Settings** → let pyRevit reload

**Verify:** open a browser and go to `http://localhost:48884/` — you should see a response, not "connection refused."

### Step 2 — Install the Revit MCP Server
This is the bridge between Claude Code and Revit. It's a separate open-source project — install it once and every skill (this one, and any future Revit skill) uses it.

Open Claude Code and say:
> *Clone https://github.com/Demolinator/revit-mcp-server into my home folder and follow its README to install it as an MCP server for Claude Code.*

Or manually: follow the README at https://github.com/Demolinator/revit-mcp-server (takes ~5 min: `uv sync`, then register with `claude mcp add`).

**Verify:** in a Claude Code session with a Revit project open, ask *"Check Revit MCP status."* You should see `Status: active, Health: healthy`.

### Step 3 — Clone this repo
In Claude Code, say:
> *Clone https://github.com/hamzaabduljabbar/autoconst-claude-bim-health-scorecard into my home folder.*

### Step 4 — Install the skill (makes it a slash command everywhere)
Ask Claude:
> *Install the bim-health-scorecard skill: copy `SKILL.md` from the cloned repo to `~/.claude/skills/bim-health-scorecard/SKILL.md`.*

Now `/bim-health-scorecard` works from any Claude Code session on this machine, forever.

### Step 5 — Install the host-side Python dep (once)
```bash
py -m pip install openpyxl
```
That's it. (`py` is the Python launcher that ships with Python for Windows.)

---

## How to run it — every time after setup

1. Open your model in Revit.
2. In any Claude Code session, type:
   > `/bim-health-scorecard`

   Or just describe what you want:
   > *Score the open Revit model.*

3. Claude reads the model, scores it, writes `outputs/BIM-Health-Scorecard-<model>.xlsx`, and hands you the file. Open it. Done.

To also **auto-fix** the safe issues (blank Assembly Codes), just say:
> *Fix the blank Uniformat codes, then re-score.*

The grade will move up live. Undo with Ctrl+Z inside Revit if you don't like the result.

To switch to the **UK / ISO 19650** profile:
> *Run the scorecard on the UK profile.*

To switch stage:
> *Run the scorecard at fabrication stage.*

---

## What's inside the scorecard — the 5 categories

| Category | Weight | What it checks |
|---|---|---|
| **Parameters** | 35% | Doors have Type Mark/size, windows have U-value, structural has material, rooms have Name/Number/Occupancy, MEP has Manufacturer/Model |
| **Classification** | 20% | OmniClass on loadable families, Assembly Code (Uniformat) on system families, valid code format |
| **Geometry** | 20% | Revit warnings count, in-place families, CAD imports (not links), unplaced rooms, duplicate marks |
| **Naming** | 15% | Family names clean + unique, levels named + unique, view/sheet naming conventions |
| **Worksharing** | 10% | Worksharing enabled, coordinates documented, view templates |

Grade bands: **A ≥ 90 · B ≥ 80 · C ≥ 70 · D ≥ 60 · F < 60**.

Weights, thresholds, and severities are all overridable per client via a `rules.custom.yaml` — that's your BEP-tuning surface.

---

## About the rules — where they come from

Every rule cites its source, and there's a **[VERIFICATION.md](VERIFICATION.md)** ledger separating what's standard-backed from what's methodology.

| Source tag | What it means |
|---|---|
| `LOD C1030`, `LOD B1010`, etc. | BIMForum LOD Specification 2024 (the actual element sections, read locally page-by-page) |
| `LOD/OC21`, `LOD/UF` | Classification codes cross-referenced in the LOD spec |
| `COBie Type`, `COBie Space` | COBie-US 2.4 template (columns verified from the actual `.xls`) |
| `ISO 19650` | UK/ISO 19650-2 Annex A naming and status codes |
| `practitioner` | Rules-of-thumb (warnings count, in-place family caps) — these are the ones clients tune |

That last row is important — a client's BEP overrides those, and that's the paid-config upsell.

---

## What it can auto-fix (and what it can't)

| Fix | Auto? | Why |
|---|---|---|
| Blank **Assembly Code** (Uniformat) on element types | ✅ Yes | Writable, per-type, fast — and it's the code US estimators price from |
| Purge unused families | ✅ Yes | Reversible, no side effects |
| Missing **OmniClass Number** | ❌ No | The parameter is read-only via API; must be set through the family editor |
| Revit warnings | ❌ No | Modeling judgment — human decision |
| In-place families | ❌ No | Should be replaced by loadable families — human call |
| Unplaced rooms | ❌ No | Room-boundary modeling — human call |

Nothing risky is ever auto-applied — anything the tool isn't 100% certain about is flagged for you to review.

---

## Folder layout

```
autoconst-claude-bim-health-scorecard/
├── README.md                       ← you are here
├── SKILL.md                        ← the Claude skill definition
├── VERIFICATION.md                 ← what's Tier 1 (verified) / 2 (sourced) / 3 (methodology)
├── engine/
│   ├── score_model.py              ← Revit-side scoring engine (IronPython, run via MCP)
│   ├── build_scorecard.py          ← Host-side Excel writer (Python + openpyxl)
│   └── autofix_assembly_code.py    ← Safe auto-fix (fills blank Uniformat codes)
├── rules/
│   ├── rules.us.yaml               ← US profile (OmniClass / COBie / Uniformat)
│   ├── rules.uk.yaml               ← UK profile (ISO 19650 / Uniclass 2015)
│   └── tables/
│       ├── classification_map.md   ← LOD-sourced Uniformat/OmniClass/Uniclass codes
│       ├── lod_data_attributes.md  ← Required params per element per LOD
│       └── cobie_columns.md        ← Verified COBie sheet columns
├── docs/
│   └── how-it-works.md             ← Deeper technical walkthrough
├── samples/
│   ├── example-scorecard-architectural.xlsx   ← real output from a 17.7k-element model
│   └── example-scorecard-structural.xlsx      ← real output from a 17k-element model
├── inputs/                         ← (empty; models stay in Revit)
└── outputs/                        ← scorecards land here
```

---

## Known limitations (honest list)

- **OmniClass can't be auto-fixed** through the current MCP — the parameter is read-only and `EditFamily` won't run inside the MCP's transaction context. Use Assembly Code (Uniformat) for classification instead — it's writable and the code US estimators actually use for cost. If you truly need native OmniClass set, that's a separate pyRevit tool.
- **MCP writes auto-commit** — there's no dry-run rollback through the MCP. But every write is on Revit's undo stack, so **Ctrl+Z** reverts.
- **Some param requirements are Tier 2** — required-parameter lists are sourced from the LOD Spec + COBie template. The COBie mandatory vs optional split is standard-defined (not color-coded in the template we parsed); see VERIFICATION.md.

---

## Contributing / rule tuning

Every threshold, weight, and severity in `rules/rules.us.yaml` and `rules/rules.uk.yaml` is meant to be edited. Copy to `rules.custom.yaml` and override anything for a specific client's BIM Execution Plan. Don't like `warnings > 100 = warn`? Change it. That's the point.

---

## License

MIT. Use it, fork it, ship it under your own brand. Only ask: don't remove the source citations from the Rule Detail tab — that's the honesty layer that makes the tool defensible.

---

## Credits

- **BIMForum LOD Specification 2024** — element data-attribute source ([bimforum.global/lod](https://bimforum.global/lod))
- **COBie / NBIMS-US v3** — asset/FM data source ([nibs.org/nbims](https://nibs.org/nbims))
- **xBimTeam** — COBie template we parsed ([github.com/xBimTeam](https://github.com/xBimTeam))
- **pyRevit** — makes talking to Revit possible ([github.com/pyrevitlabs/pyRevit](https://github.com/pyrevitlabs/pyRevit))
- **Revit MCP Server** — the bridge ([github.com/Demolinator/revit-mcp-server](https://github.com/Demolinator/revit-mcp-server))
