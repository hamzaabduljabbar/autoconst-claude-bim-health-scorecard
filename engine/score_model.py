# encoding: utf-8
# =============================================================================
# BIM Health Scorecard - scoring engine v1.3
# Runs inside Revit via the Revit MCP execute_revit_code (IronPython 2.7).
#
# NEW in v1.3: every rule carries a verified `src` citation, and category rules
# reflect the source split proven from primary docs (see rules/tables/):
#   - size / material / type / operation      -> LOD Spec 2024   (src=LOD)
#   - Manufacturer / Model / Serial / Cost    -> COBie sheets    (src=COBie)
#   - Fire Rating                             -> na_allowed (fire-rated only)
#   - asset/FM data is design-stage advisory, becomes required at operations
#     stage (stage-based severity).
# =============================================================================
import re
from pyrevit import revit, DB
doc = revit.doc

STAGE = "design"                      # design | fabrication | operations
SEV_FACTOR = {"fail": 1.0, "warn": 0.5, "info": 0.0}
CAT_WEIGHTS = {"naming": 0.15, "parameters": 0.35, "classification": 0.20,
               "geometry": 0.20, "worksharing": 0.10}
GRADE = [("A", 90), ("B", 80), ("C", 70), ("D", 60), ("F", 0)]
BIC = DB.BuiltInCategory

def is_empty(v):
    return v is None or unicode(v).strip() in ("", "None")

def pget(elem, name):
    p = elem.LookupParameter(name)
    if p is None:
        tid = elem.GetTypeId()
        if tid and tid != DB.ElementId.InvalidElementId:
            t = doc.GetElement(tid)
            if t:
                p = t.LookupParameter(name)
    if p is None:
        return None
    try:
        v = p.AsString()
        if v is None or v == "":
            vs = p.AsValueString()
            if vs is not None and vs != "":
                v = vs
        return v
    except:
        return None

def collect(bic):
    return list(DB.FilteredElementCollector(doc).OfCategory(bic)
                .WhereElementIsNotElementType().ToElements())

def resolve_sev(r):
    sbs = r.get("severity_by_stage")
    return sbs.get(STAGE, r.get("severity", "warn")) if sbs else r.get("severity", "warn")

RESULTS = []
def add(cat, rid, name, weight, sev, passrate, fails, src="-", na=False):
    RESULTS.append(dict(cat=cat, id=rid, name=name, weight=weight, severity=sev,
                        passrate=passrate, fails=fails, src=src, na=na))

def param_rule(r):
    els = collect(r["bic"])
    if not els:
        return
    fails = []
    for e in els:
        miss = [p for p in r["params"] if is_empty(pget(e, p))]
        if miss:
            fails.append((e.Id.IntegerValue, ",".join(miss)))
    sev = "info" if r.get("na_allowed") else resolve_sev(r)
    add(r["cat"], r["id"], r["name"], r["weight"], sev,
        1.0 - len(fails) / float(len(els)), fails, src=r.get("src", "-"),
        na=r.get("na_allowed", False))

# --- PARAMETER RULES (each tagged with its verified source) ------------------
PARAM_RULES = [
    # Doors: LOD C1030 mandates type/size/operation; Fire Rating na_allowed
    dict(cat="parameters", id="P-06", name="Doors: Type Mark/Width/Height",
         bic=BIC.OST_Doors, params=["Type Mark", "Width", "Height"], weight=2,
         severity="fail", src="LOD C1030"),
    dict(cat="parameters", id="P-06b", name="Door Fire Rating coverage",
         bic=BIC.OST_Doors, params=["Fire Rating"], weight=1, na_allowed=True,
         src="LOD/na"),
    dict(cat="parameters", id="P-06c", name="Door Operation type",
         bic=BIC.OST_Doors, params=["Operation"], weight=1, na_allowed=True,
         src="LOD C1030"),
    # Windows: LOD C1020 mandates size + U-value + operation
    dict(cat="parameters", id="P-07", name="Windows: Type Mark/Width/Height",
         bic=BIC.OST_Windows, params=["Type Mark", "Width", "Height"], weight=1,
         severity="warn", src="LOD C1020"),
    dict(cat="parameters", id="P-07b", name="Window U-value coverage",
         bic=BIC.OST_Windows, params=["Analytic Construction"], weight=1,
         na_allowed=True, src="LOD C1020"),
    # Structural: LOD B1010 mandates size(TypeMark)+material; TypeMark stage-based
    dict(cat="parameters", id="P-09", name="Struct framing: Structural Material",
         bic=BIC.OST_StructuralFraming, params=["Structural Material"], weight=2,
         severity="fail", src="LOD B1010"),
    dict(cat="parameters", id="P-09c", name="Struct columns: Structural Material",
         bic=BIC.OST_StructuralColumns, params=["Structural Material"], weight=2,
         severity="fail", src="LOD B1010"),
    dict(cat="parameters", id="P-09m", name="Struct members: Type Mark (fab ID)",
         bic=BIC.OST_StructuralFraming, params=["Type Mark"], weight=2,
         na_allowed=True, severity_by_stage={"design": "info", "fabrication": "fail"},
         src="LOD B1010"),
    # MEP asset data: COBie Type sheet (Manufacturer/Model). Design=advisory,
    # operations=required. src=COBie.
    dict(cat="parameters", id="P-04h", name="Mech equip: Manufacturer/Model",
         bic=BIC.OST_MechanicalEquipment, params=["Manufacturer", "Model"], weight=2,
         severity_by_stage={"design": "info", "operations": "fail"}, na_allowed=(STAGE == "design"),
         src="COBie Type"),
    dict(cat="parameters", id="P-04p", name="Plumbing fix: Manufacturer/Model",
         bic=BIC.OST_PlumbingFixtures, params=["Manufacturer", "Model"], weight=1,
         severity_by_stage={"design": "info", "operations": "fail"}, na_allowed=(STAGE == "design"),
         src="COBie Type"),
    dict(cat="parameters", id="P-04l", name="Lighting: Manufacturer/Model",
         bic=BIC.OST_LightingFixtures, params=["Manufacturer", "Model"], weight=1,
         severity_by_stage={"design": "info", "operations": "fail"}, na_allowed=(STAGE == "design"),
         src="COBie Type"),
    # Rooms: COBie Space sheet (Name/Category/Floor)
    dict(cat="parameters", id="P-10", name="Rooms: Name/Number/Occupancy",
         bic=BIC.OST_Rooms, params=["Name", "Number", "Occupancy"], weight=2,
         severity="fail", src="COBie Space"),
]
for r in PARAM_RULES:
    param_rule(r)

rooms = collect(BIC.OST_Rooms)
if rooms:
    f = []
    for r in rooms:
        try: a = r.Area
        except: a = 0
        if r.Location is None or a is None or a <= 0:
            f.append((r.Id.IntegerValue, "unplaced/area0"))
    add("parameters", "P-11", "Rooms placed and area>0", 2, "fail",
        1.0 - len(f) / float(len(rooms)), f, src="COBie Space")

# --- CLASSIFICATION (category-aware; codes verified from LOD spec) -----------
OMNI_RE = re.compile(r'^[0-9]{2}(\.[0-9]{2})+$')
LOADABLE = [("Doors", BIC.OST_Doors), ("Windows", BIC.OST_Windows),
            ("Plumbing", BIC.OST_PlumbingFixtures), ("Lighting", BIC.OST_LightingFixtures),
            ("Furniture", BIC.OST_Furniture), ("Casework", BIC.OST_Casework),
            ("Framing", BIC.OST_StructuralFraming), ("Columns", BIC.OST_StructuralColumns),
            ("Foundations", BIC.OST_StructuralFoundation)]
SYSTEM = [("Walls", BIC.OST_Walls), ("Floors", BIC.OST_Floors),
          ("Roofs", BIC.OST_Roofs), ("Ceilings", BIC.OST_Ceilings)]
for lab, bic in LOADABLE:
    els = collect(bic)
    if not els: continue
    miss = [(e.Id.IntegerValue, "no OmniClass") for e in els if is_empty(pget(e, "OmniClass Number"))]
    acm = [(e.Id.IntegerValue, "no Assembly Code") for e in els if is_empty(pget(e, "Assembly Code"))]
    n = float(len(els))
    add("classification", "C-01/" + lab, "OmniClass (%s)" % lab, 2, "fail", 1.0 - len(miss) / n, miss, src="LOD/OC21")
    add("classification", "C-04/" + lab, "Uniformat (%s)" % lab, 1, "warn", 1.0 - len(acm) / n, acm, src="LOD/Uniformat")
for lab, bic in SYSTEM:
    els = collect(bic)
    if not els: continue
    miss = [(e.Id.IntegerValue, "no Assembly Code") for e in els if is_empty(pget(e, "Assembly Code"))]
    add("classification", "C-05/" + lab, "Uniformat system (%s)" % lab, 2, "fail",
        1.0 - len(miss) / float(len(els)), miss, src="LOD/Uniformat")

# --- GEOMETRY ----------------------------------------------------------------
def tpass(c, wa=None, fa=None, tg=0):
    if fa is not None and c > fa: return 0.0
    if wa is not None and c > wa: return 0.5
    return 1.0 if c <= tg else 0.5
w = doc.GetWarnings()
add("geometry", "G-01", "Revit warnings", 3, "fail", tpass(len(w), 100, 1000),
    [(0, "%d warnings" % len(w))] if w else [], src="practitioner")
ip = [f for f in DB.FilteredElementCollector(doc).OfClass(DB.Family) if f.IsInPlace]
add("geometry", "G-02", "In-place families", 2, "fail", tpass(len(ip), 10, None, 0),
    [(f.Id.IntegerValue, f.Name) for f in ip], src="practitioner")
im = [i for i in DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).ToElements() if not i.IsLinked]
add("geometry", "G-03", "Imported CAD", 2, "fail", 1.0 if not im else 0.0, [], src="practitioner")

# --- NAMING ------------------------------------------------------------------
lv = collect(BIC.OST_Levels)
if lv:
    seen, bad = {}, []
    for l in lv:
        nm = getattr(l, "Name", "") or ""
        if is_empty(nm): bad.append((l.Id.IntegerValue, "unnamed"))
        elif nm in seen: bad.append((l.Id.IntegerValue, "dup"))
        seen[nm] = 1
    add("naming", "N-03", "Levels named + unique", 1, "warn", 1.0 - len(bad) / float(len(lv)), bad, src="practitioner")
fams = list(DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements())
if fams:
    IL = re.compile(r'[\\/:*?"<>|{}]'); nm2 = {}; bf = []
    for f in fams:
        nm = getattr(f, "Name", "") or ""
        if IL.search(nm): bf.append((f.Id.IntegerValue, "illegal"))
        if nm in nm2: bf.append((f.Id.IntegerValue, "dup"))
        nm2[nm] = 1
    add("naming", "N-01", "Family names clean+unique", 2, "fail", 1.0 - len(bf) / float(len(fams)), bf, src="practitioner")

# --- WORKSHARING -------------------------------------------------------------
if doc.IsWorkshared:
    add("worksharing", "W-01", "Worksharing enabled", 2, "warn", 1.0, [], src="practitioner")
else:
    add("worksharing", "W-01", "Worksharing (standalone N/A)", 2, "info", 1.0, [], src="practitioner", na=True)

# --- SCORING -----------------------------------------------------------------
def letter(s):
    for g, lo in GRADE:
        if s >= lo: return g
    return "F"
cat_scores = {}
for cat in CAT_WEIGHTS:
    rules = [r for r in RESULTS if r["cat"] == cat and SEV_FACTOR.get(r["severity"], 0) > 0]
    if not rules: continue
    wsum = sum(r["weight"] * SEV_FACTOR[r["severity"]] for r in rules)
    psum = sum(r["weight"] * SEV_FACTOR[r["severity"]] * r["passrate"] for r in rules)
    cat_scores[cat] = 100.0 * psum / wsum if wsum else 100.0
overall = (sum(CAT_WEIGHTS[c] * cat_scores[c] for c in cat_scores)
           / sum(CAT_WEIGHTS[c] for c in cat_scores)) if cat_scores else 0.0

print("=" * 66)
print("BIM HEALTH SCORECARD v1.3 (stage=%s) - %s" % (STAGE, doc.Title))
print("=" * 66)
print("OVERALL: %.1f / 100    GRADE: %s" % (overall, letter(overall)))
print("-" * 66)
for cat in ["naming", "parameters", "classification", "geometry", "worksharing"]:
    if cat in cat_scores:
        print("%-15s %5.1f (%s)  wt %.0f%%" % (cat.upper(), cat_scores[cat],
                                               letter(cat_scores[cat]), CAT_WEIGHTS[cat] * 100))
print("-" * 66)
print("%-12s %-30s %-14s %s" % ("rule", "check", "source", "pass/fails"))
for r in RESULTS:
    tag = " [adv]" if r["na"] else ""
    print("  %-11s %-30s %-13s %3.0f%% (%d)%s" % (
        r["id"], r["name"][:30], r["src"], r["passrate"] * 100, len(r["fails"]), tag))
print("=" * 66)
