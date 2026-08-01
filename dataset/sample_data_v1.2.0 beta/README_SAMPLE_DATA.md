# Myanmar Demonstration Construction Noise Dataset

This is a fictional, synthetic dataset created for testing the QGIS Noise Prediction plugin.

## Location
The geometries are positioned near Bago Region, Myanmar for demonstration only.
They do not represent a real construction project or real sensitive receptors.

## Coordinate Reference System
WGS 84 / UTM zone 47N (EPSG:32647)

## Layers
- Construction_Sources.shp: 8 construction noise source points
- Receptors.shp: 15 receptor points
- Barrier.shp: 3 simplified barrier lines
- Site_Boundary.shp: fictional construction-site polygon
- Road.shp: contextual roads
- Buildings.shp: contextual building footprints

## Suggested plugin field mapping
Construction sources:
- Source ID: source_id
- Equipment: equipment
- Activity: activity
- Source level: level_db
- Usage percentage: use_pct
- Operating hours: hours_day
- Source height: height_m

Receptors:
- Receptor ID: recept_id
- Receptor name: name
- Receptor height: height_m
- Indicative threshold: threshold

## Important note
All acoustic values are illustrative and are not verified BS 5228 reference values.
They are provided only to test data loading, field mapping, cumulative calculations,
output creation, and visualization.


## Manual correction fields for v0.5.0 Beta

- `screen_db`: user-defined screening attenuation in dB, entered as a positive reduction.
  Suggested demonstration values: 0, 5, or 10 dB.
- `reflect_db`: user-defined reflection correction in dB, entered as a positive addition.
  Suggested demonstration values: 0, 1, or 2 dB.
- `corr_note`: brief explanation of the selected assumptions.

These values are illustrative only. Version 0.5.0 Beta does not derive screening or
reflection automatically from geometry. Users must apply professional judgement.

A single source-level correction is applied uniformly in this sample. In reality,
screening and reflection can vary for every source-receptor path. Future versions
should calculate these effects using source, receptor, barrier, terrain, and building
geometry.
