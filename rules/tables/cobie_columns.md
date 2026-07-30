# COBie worksheet columns (verified) + mandatory subset

Column names transcribed directly from the actual **COBie-US 2.4 template**
(xBimTeam/XbimExchange `COBie-US-2_4-template.xls`, read with Python/xlrd).
The 20 worksheets: Instruction, Contact, Facility, Floor, Space, Zone, Type,
Component, System, Assembly, Connection, Spare, Resource, Job, Impact, Document,
Attribute, Coordinate, Issue, PickLists.

VERIFICATION NOTE: this template renders all header cells gray (no yellow
color-coding), so the mandatory/optional split below follows the COBie standard
(NBIMS-US v3), not this file's fill colors. The COLUMN NAMES are Tier-1 verified
from the file; the MANDATORY flag is Tier-2 (standard-defined). To lock the
mandatory split to Tier-1, obtain a color-coded COBie template.

Legend: **bold** = mandatory per COBie standard; rest = optional/as-available.

## Contact (19)
**Email, CreatedBy, CreatedOn, Category, Company, Phone**, ExternalSystem,
ExternalObject, ExternalIdentifier, Department, OrganizationCode, GivenName,
FamilyName, Street, PostalBox, Town, StateRegion, PostalCode, Country

## Facility (22)
**Name, CreatedBy, CreatedOn, Category, ProjectName, SiteName, LinearUnits,
AreaUnits, VolumeUnits, CurrencyUnit, AreaMeasurement**, ExternalSystem,
ExternalProjectObject, ExternalProjectIdentifier, ExternalSiteObject,
ExternalSiteIdentifier, ExternalFacilityObject, ExternalFacilityIdentifier,
Description, ProjectDescription, SiteDescription, Phase

## Floor (10)
**Name, CreatedBy, CreatedOn, Category**, ExtSystem, ExtObject, ExtIdentifier,
Description, Elevation, Height

## Space (13)
**Name, CreatedBy, CreatedOn, Category, FloorName, Description**, ExtSystem,
ExtObject, ExtIdentifier, RoomTag, UsableHeight, GrossArea, NetArea

## Zone (9)
**Name, CreatedBy, CreatedOn, Category, SpaceNames**, ExtSystem, ExtObject,
ExtIdentifier, Description

## Type (35)
**Name, CreatedBy, CreatedOn, Category, Description, AssetType, Manufacturer,
ModelNumber, WarrantyGuarantorParts, WarrantyDurationParts,
WarrantyGuarantorLabor, WarrantyDurationLabor, WarrantyDurationUnit,
ReplacementCost, ExpectedLife, DurationUnit, WarrantyDescription, NominalLength,
NominalWidth, NominalHeight, ModelReference**, ExtSystem, ExtObject,
ExtIdentifier, Shape, Size, Color, Finish, Grade, Material, Constituents,
Features, AccessibilityPerformance, CodePerformance, SustainabilityPerformance

## Component (15)
**Name, CreatedBy, CreatedOn, TypeName, Space, Description**, ExtSystem,
ExtObject, ExtIdentifier, SerialNumber, InstallationDate, WarrantyStartDate,
TagNumber, BarCode, AssetIdentifier

## System (9)
**Name, CreatedBy, CreatedOn, Category, ComponentNames**, ExtSystem, ExtObject,
ExtIdentifier, Description

---
## Mapping to scorecard rules
- Type.Manufacturer / ModelNumber -> door/MEP "Manufacturer","Model" param rules.
- Type.Category -> classification (OmniClass/Uniclass) rule.
- Component.Space -> "element assigned to a room/space" rule.
- Component.TypeName -> every instance must resolve to a Type.
- Space.Name/Category/FloorName -> room Name/Number/Occupancy + floor rules.
- Type.WarrantyGuarantorParts/DurationParts, ReplacementCost, ExpectedLife ->
  handover/FM param rules (fabrication/operations stage only).
