# encoding: utf-8
# =============================================================================
# BIM Health Scorecard - Assembly Code (Uniformat) auto-fix
# Runs inside Revit via execute_revit_code (IronPython 2.7).
#
# Fills BLANK "Assembly Code" (Uniformat II) on element TYPES only (never
# overwrites an existing value). For each category it derives the fill value
# from that category's OWN most-common existing code (modal), so the model
# stays internally consistent; falls back to a Uniformat default if the whole
# category is blank.
#
# WHY Assembly Code and not OmniClass:
#   - "OmniClass Number" is READ-ONLY via param write (set through family
#     classification only) -> cannot be batch-filled here.
#   - "Assembly Code" IS writable, per-type, and is the code US estimators
#     price from. Verified writable on the Snowdon sample models.
#
# TRANSACTION NOTE: the MCP endpoint auto-wraps this in a Revit transaction and
#   commits it. There is no in-call rollback -> writes persist. They ARE on the
#   Revit undo stack, so the user reverts with Ctrl+Z. Only run on approval.
#
# Extend CATS / DEFAULT to cover more categories per discipline.
# =============================================================================
from pyrevit import revit, DB
doc = revit.doc

def is_empty(v):
    return v is None or unicode(v).strip() in ("", "None")

# Uniformat II Level-3 fallbacks (used only if a whole category is blank).
# Doors resolve by Function at call time (Exterior->B2030, Interior->C1020).
DEFAULT = {
    "Framing": "B1010", "Columns": "B1010", "Foundations": "A1010",
    "Windows": "B2020", "Plumbing Fixtures": "D2010",
    "Lighting Fixtures": "D5020", "Casework": "E2010", "Furniture": "E2020",
}
CATS = [
    ("Framing", DB.BuiltInCategory.OST_StructuralFraming),
    ("Columns", DB.BuiltInCategory.OST_StructuralColumns),
    ("Foundations", DB.BuiltInCategory.OST_StructuralFoundation),
    ("Windows", DB.BuiltInCategory.OST_Windows),
    ("Plumbing Fixtures", DB.BuiltInCategory.OST_PlumbingFixtures),
    ("Lighting Fixtures", DB.BuiltInCategory.OST_LightingFixtures),
    ("Casework", DB.BuiltInCategory.OST_Casework),
    ("Furniture", DB.BuiltInCategory.OST_Furniture),
]

APPLY = True   # set False for a dry-run preview (reports targets, writes nothing)

filled_total = 0
for lab, bic in CATS:
    types = list(DB.FilteredElementCollector(doc).OfCategory(bic)
                 .WhereElementIsElementType().ToElements())
    if not types:
        continue
    freq, blanks = {}, []
    for t in types:
        ac = t.LookupParameter("Assembly Code")
        if ac is None or ac.IsReadOnly:
            continue
        v = ac.AsString()
        if is_empty(v):
            blanks.append(t)
        else:
            freq[v] = freq.get(v, 0) + 1
    if not blanks:
        continue
    fill = max(freq, key=freq.get) if freq else DEFAULT.get(lab, "")
    src = "modal" if freq else "default"
    print("%-18s blanks=%d fill='%s' (%s)" % (lab, len(blanks), fill, src))
    if APPLY and fill:
        for t in blanks:
            t.LookupParameter("Assembly Code").Set(fill)
            filled_total += 1

print("-" * 50)
print("%s: %d type definitions filled  (Ctrl+Z reverts)" % (
    "APPLIED" if APPLY else "DRY-RUN", filled_total))
