# Classification code map — Uniformat / OmniClass / Uniclass

Authoritative element classification codes, transcribed from the **BIMForum LOD
Specification 2024 Part I** (each element section prints all three codes plus
MasterFormat cross-refs). This is the source of truth for the classification
rules and the Assembly Code (Uniformat) auto-fix defaults — they are now
standard-backed, not guessed.

Source: LOD-Spec-2024-Part-I-official-English.pdf (read locally, pp. 6–7 TOC +
element pages). Format in spec: `UNIFORMAT / OMNICLASS / UNICLASS  Title`.

| Element | Uniformat | OmniClass | Uniclass 2015 |
|---|---|---|---|
| Standard Foundations | A1010 | 21-01 10 10 | Ss 20 05 |
| Special Foundations | A1020 | 21-01 10 20 | Ss 20 05 |
| Walls for Subgrade Enclosures | A2010 | 21-01 20 10 | Ss 20 60 |
| Standard Slabs-on-Grade | A4010 | 21-01 40 10 | Pr 20 85 14 16 |
| Structural Slabs-on-Grade | A4020 | 21-01 40 20 | Pr 20 85 14 16 |
| Floor Construction (framing/beams) | B1010 | 21-02 10 10 | Ss 30 12 |
| Roof Construction | B1020 | 21-02 10 20 | Ss 30 10 |
| Stairs | B1080 | 21-02 10 80 | Ss 35 |
| Exterior Walls | B2010 | 21-02 20 10 10 | EF 25 10 |
| Exterior Wall Veneer | B2010.10 | 21-02 20 10 10 | EF 25 10 |
| Exterior Windows | B2020 | 21-02 20 20 | Ss 25 30 95 26 |
| Exterior Doors and Grilles | B2050 | 21-02 20 50 | Ss 25 30 20 |
| Roofing | B3010 | 21-02 30 10 | Ss 30 10 |
| Interior Partitions | C1010 | 21-03 10 10 | Ss 25 10 30 |
| Interior Windows | C1020 | 21-03 10 20 | Ss 25 30 95 41 |
| Interior Doors | C1030 | 21-03 10 30 | Ss 25 30 20 25 |
| Wall Finishes | C2010 | 21-03 20 10 | Ss 25 45 |
| Flooring | C2030 | 21-03 20 30 | Ss 30 42 |
| Ceiling Finishes | C2050 | 21-03 20 50 | Ss 30 47 |
| Vertical Conveying (elevators) | D1010 | 21-04 10 10 | Ss 80 50 |
| Plumbing | D20 | 21-04 20 | – |
| HVAC / Mechanical | D30 | 21-04 30 | Ss 60 |
| Facility Fuel Systems | D3010 | 21-04 30 10 | Ss 55 50 |
| Lighting | D5040 | 21-04 50 40 | Ss 70 80 |
| Steel Framing Column | B1010.10.30 | 21-02 10 10 10 30 | – |
| Interior Doors (swinging) | C1030.10 | 21-03 10 30 10 | Ss 25 30 20 25 |

Notes:
- Uniformat is the ELEMENTAL cost code US estimators price from; it is the
  writable, auto-fixable `Assembly Code` in Revit.
- OmniClass 21 = Elements table (mirrors Uniformat). Revit's "OmniClass Number"
  on loadable families is usually from OmniClass 23 (Products), a different
  table — do not conflate the two when validating codes.
- Uniclass 2015 = UK profile classification (swap in for the UK rulebook).
- Codes for interior doors/windows differ from exterior — a category-default
  auto-fill must resolve interior vs exterior (doors: use Revit `Function`).
