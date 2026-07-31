# encoding: utf-8
# Color-splash: paints failing elements in the active view.
# Reads outputs/scorecard_data.json and colors each rule's failing elements
# by severity so the user can literally SEE what's wrong.
#
# Run via mcp__revit__execute_revit_code AFTER the scorecard has run.
# Undo with the color reset (mcp__revit__clear_colors) or run this with CLEAR = True.
import json
from pyrevit import revit, DB
doc = revit.doc

CLEAR = False   # True = wipe overrides and exit

DATA = r"C:\Users\Hamza\autoconst-claude-bim-health-scorecard\outputs\scorecard_data.json"

# severity -> RGB
COLORS = {
    "fail":  DB.Color(220, 40, 40),    # red
    "warn":  DB.Color(240, 170, 40),   # orange
    "info":  DB.Color(240, 220, 60),   # yellow (advisory)
}

view = doc.ActiveView

def clear():
    ogs = DB.OverrideGraphicSettings()
    for e in DB.FilteredElementCollector(doc, view.Id).WhereElementIsNotElementType().ToElements():
        try: view.SetElementOverrides(e.Id, ogs)
        except: pass

if CLEAR:
    clear()
    print("cleared overrides on view:", view.Name)
else:
    clear()  # start clean
    with open(DATA) as f:
        data = json.load(f)
    counts = {"fail": 0, "warn": 0, "info": 0}
    for rule in data["rules"]:
        sev = rule["sev"]
        if sev not in COLORS: continue
        ogs = DB.OverrideGraphicSettings()
        ogs.SetProjectionLineColor(COLORS[sev])
        ogs.SetSurfaceForegroundPatternColor(COLORS[sev])
        # solid fill pattern
        for p in DB.FilteredElementCollector(doc).OfClass(DB.FillPatternElement):
            if p.GetFillPattern().IsSolidFill:
                ogs.SetSurfaceForegroundPatternId(p.Id); break
        for eid, _issue in rule["fails"]:
            if eid == 0: continue
            try:
                view.SetElementOverrides(DB.ElementId(eid), ogs)
                counts[sev] += 1
            except: pass
    print("colored: %d red (fail), %d orange (warn), %d yellow (info)" %
          (counts["fail"], counts["warn"], counts["info"]))
    print("view:", view.Name)
    print("Tip: run again with CLEAR=True to reset.")
