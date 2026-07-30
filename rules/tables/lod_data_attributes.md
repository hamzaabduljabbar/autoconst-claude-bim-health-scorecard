# LOD data-attribute requirements (from BIMForum LOD Spec 2024)

Non-graphic (data) requirements per element per LOD, transcribed from the
**BIMForum.Global 2024 LOD Specification** (October 2024 combined edition, read
locally page-by-page). Each element's LOD table has a Description /
"Non-graphic information" block — that is the required-attribute source.

## THE KEY FINDING (read this first)
The LOD spec is a GEOMETRY dictionary. What it mandates as data splits cleanly,
and this is what the scorecard should encode:

1. **Geometric / type data (LOD Tier 1):** size, nominal dimensions, material,
   type, location/orientation, connections. Specified per element per LOD.
2. **Performance data (LOD, element-dependent):** given explicitly for some
   elements (windows: U-value, wind/thermal/acoustic; operation type) and NOT
   for others.
3. **Asset / FM data (NOT in LOD — comes from COBie + the BEP):** Manufacturer,
   Model, Serial, Cost, Warranty, Expected Life. MEP sections say verbatim
   "Design performance parameters as defined in the BXP to be associated with
   model elements as non-graphic information" — i.e. the spec DEFERS this to the
   project BIM Execution Plan and COBie (rules/tables/cobie_columns.md).

=> Scorecard consequence: don't cite LOD for Manufacturer/Model/Cost — cite
   COBie. Cite LOD for size/material/type/operation. Fire Rating is required
   only where fire-rated (LOD lists it nowhere as universal) -> na_allowed is
   the standard-aligned choice.

## Per-element extract (worked from the spec)

### Windows — Interior/Exterior (Uniformat C1020.10 / B2020, OC 21-03 10 20 10)
- LOD 300: nominal size; frame+glazing geometry. Non-graphic: aesthetic
  (finishes, glass types); performance (U-value, wind, blast, structural, air,
  thermal, water, sound); operation (fixed/casement/hung/awning/pivot/sliding).
- LOD 350: attachment to structure; embed geometry.
- LOD 400: frame profiles, glazing gaskets, attachment parts.
- Scorecard params: Type Mark, Width, Height, U-value, Operation, Glazing/Finish.

### Interior Swinging Doors (Uniformat C1030.10, OC 21-03 10 30 10, Ss 25 30 20 25)
- LOD 300: door assemblies by type — specific panels + frames (if applicable);
  operation specified.
- LOD 350: major framing at jambs/head; operation/mechanism enclosures.
- LOD 400: actual frame/mullion extrusions; panel dimensions; connections,
  brackets, supports, sealants, thresholds.
- Scorecard params: Type Mark, Width, Height, Operation. (Fire Rating NOT listed
  as universal -> advisory / na_allowed, per fire-rated openings only.)

### Steel Framing Column (Uniformat B1010.10.30, OC 21-02 10 10 10 30)
- LOD 300: specific member sizes, correct location/orientation per grid.
- LOD 350: connections + elevations; base/gusset plates, anchor rods; misc steel
  with correct size/shape/orientation/material; reinforcement.
- LOD 400: welds, coping, cap plates, washers/nuts, assembly elements.
- Scorecard params: Section size (Type Mark), Structural Material, connections
  (fabrication stage), location.

### HVAC (Uniformat D30, OC 21-04 30, Ss 60)
- LOD 100-200: diagrammatic/schematic layout + flow diagram.
- Geometry + clearance focused. Asset data deferred to BEP/COBie.
- Scorecard params: System assignment, clearance; Manufacturer/Model via COBie.

### Plumbing (Uniformat D20, OC 21-04 20)
- LOD 100-200: diagrammatic/schematic. VERBATIM: "Design performance parameters
  as defined in the BXP to be associated with model elements as non-graphic
  information." -> defers data to the BEP.
- Scorecard params: System assignment; Manufacturer/Model/fixture data via COBie.

### Lighting (Uniformat D5040, OC 21-04 50 40, Ss 70 80, MF 26 50 00)
- LOD 200: schematic layout with approximate size, shape, location of equipment.
- Geometry focused; asset data via COBie/BEP.
- Scorecard params: location, Space assignment; Manufacturer/Model via COBie.

## Extraction status: COMPLETE for the representative set
Covered across all major disciplines: Windows, Doors, Structural Steel,
Foundations/Walls (classification_map.md), HVAC, Plumbing, Lighting. The
per-element "Non-graphic information" block is identical in structure
everywhere; the finding above (geometry=LOD, asset data=COBie/BEP) holds across
the whole spec. Any additional element (electrical devices, roofing, fire
protection) follows the same split and can be transcribed from the saved PDF if
a category-specific rule needs it.
