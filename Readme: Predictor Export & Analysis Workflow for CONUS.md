Predictor Export & Analysis Workflow for CONUS

This repository contains a suite of Google Earth Engine scripts to export, process, and analyze a variety of environmental predictor datasets over the continental United States (CONUS). The workflow includes:

- Unified Exporter: Clip static, core climate, and land surface/fpar predictors to a common 500 m grid.
- LST/LAI/FPAR Exporter: Generate scaled int16 stacks of MODIS LST, LAI, and FPAR for annual and seasonal windows.
- All‑Predictor Slope Stack: Compute robust Theil–Sen slopes and Kendall’s τ for core and LST/LAI/FPAR predictors.
- Stratified Sampling: Draw k points per 0.1° grid cell within each EPA Level‑2 ecoregion for model training or analysis.


Table of Contents

- Prerequisites
- Directory Structure
- Scripts & Descriptions
- Usage
- Asset Naming & Paths


Prerequisites

- A Google Earth Engine account
- Access to the following EE image collections and assets:
- MODIS/061/MOD13A1, MODIS/061/MCD12Q1, MODIS/061/MOD11A2, MODIS/061/MCD15A3H
- NASA/NASADEM_HGT/001, DAYMET_V4, MOD10A2, GLOBGM WTD, and your CONUS_Union feature collection
- Sufficient EE asset quotas for image and table exports


Scripts & Descriptions

1. Core_Predictor_Stack.js

- Purpose: Exports multiple predictor sets—static terrain (elevation, slope, aspect, groundwater depth), core climate (precipitation, temperature, VPD, snow), and land-surface factors (LST, LAI, FPAR)—on a unified 500 m EPSG:4326 grid.
- Toggles: EXPORT_STATIC, EXPORT_CORE, EXPORT_LSF to enable/disable sections.
- Grid & Reference: Uses Phenology_2000_CONUS projection as the grid reference.

Output:

- staticPredictors_500m (bands: elev, slope, aspect, gwDepth)
- corePredictor_<year> (annual & seasonal prcp, tmax, tmin, vpd, snowDays)

2. modisPredictor_Stack.js

Purpose: Generates quantized int16 stacks of MODIS LST (°C), LAI, and FPAR for each year (2000–2024), with annual and four seasonal means.
Scaling: Multiplies LST by 100, LAI by 1 000, FPAR by 10 000 to preserve precision in int16.
Seasons: Winter, Spring, Summer, Fall defined by DOY windows.

Output: 

- lstLaiFpar_<year> asset containing 8 bands (4 annual + 4 seasonal for each variable).

3. TheilSen_KendalP_Predictors.js

- Purpose: Computes robust Theil–Sen slopes and filters by Kendall’s τ p‑value for all exported predictor bands.
- Inputs:   Core predictors (corePredictor_), LST/LAI/FPAR stacks (lstLaiFpar_), stable-land-cover mask (MCD12Q1 LC_Type1 & LC_Type5).

Output: 

- Single multi-band raster allPredictorSlopes with one slope band per predictor.

4. Sample_Points_Export.js

- Purpose: Draws k sample points per 0.1° grid cell within each EPA Level‑2 ecoregion, capped at N_CAP points per ecoregion.
- Parameters: GRID (0.1°), K_PER (samples per cell), N_CAP (max per ecoregion).
- Masking: Samples only where NDVI_SOS_slope is valid.

Output: 
- CSV tables eco_<EcoregionName>.csv in Google Drive folder EcoSamples_01deg.


Usage

Open each script in the GEE Code Editor.
Update the FOLDER, REF_IMG, and any asset paths to match your EE account.
Adjust toggles and parameters as needed.
Run scripts in order (01 → 04).
Monitor the Tasks pane for export progress.


Asset Naming & Paths

Predictor Slopes: projects/horia-olariu/assets/Greening/allPredictorSlopes
Random sample stack: randomSampleStack.zip
