Phenology Mapping Pipeline for CONUS

This repository contains a sequential workflow of Earth Engine scripts to compute and export multi‐year phenology metrics (Start of Season, Peak of Season, End of Season), clean and mask outputs, derive robust trends, and assemble a final phenology stack for the continental United States (CONUS).


Table of Contents

Overview
Prerequisites
Directory Structure
Script Pipeline
Usage
Outputs
Asset Naming & Paths
Customization
License
Contact


Overview

This pipeline computes phenological metrics from MODIS MOD13A1 NDVI/EVI (500 m) over CONUS for years 2000–2024. The workflow comprises:
- SOS: Identify Start of Season by fitting a 6th‐order polynomial and threshold detection.
- POS: Compute Peak of Season start/end dates using an 80 % plateau method.
- EOS: Determine End of Season via largest negative VI drop and polynomial fitting.
- Clean: Mask unwanted land‐cover classes and invalid pixels for SOS/EOS and POS.
- Length: Add POS length bands (POSend – POSstart + 1).
- Trends: Calculate robust Theil–Sen slopes and Kendall’s τ for each phenology band.
- Stack: Merge cleaned SOS, POS, EOS into a 10‑band annual phenology asset.
- Each step exports assets to your EE account for downstream analysis.


Prerequisites

Google Earth Engine account.
Access to MODIS/061/MOD13A1 and MODIS/061/MCD12Q1 collections.
EE asset folder for outputs (e.g., users/horia/assets/Greening/).
CONUS_Union feature collection for study area.


Script Pipeline

1. 01_SOS_CONUS.js (Start of Season)

- Builds baseline seasonal curve (3‑day rolling mean) from 2000–2024.
- Derives green‑up thresholds via day‑to‑day ratio and qualityMosaic.
- Fits 6th‑order polynomial to daily VI time series (Jan–Oct 1).
- Extracts SOS (DOY 0–273) where curve ≥ threshold; assigns –999 otherwise.
- Exports yearly SOS_<year> assets with bands NDVI_SOS and EVI_SOS.

2. 02_POS_CONUS.js (Peak of Season)

- Uses same baseline and polynomial helpers as SOS.
- Defines plateau threshold at 80 % of annual VI max for DOY 60–334.
- Identifies POS start (first DOY ≥ threshold) and end (last DOY ≥ threshold).
- Exports POS_<year>_CONUS assets with four bands: NDVI_POSstart, NDVI_POSend, EVI_POSstart, EVI_POSend.

3. 03_EOS_CONUS.js (End of Season)

- Computes largest negative VI drop from 3‑day baseline to define senescence threshold.
- Fits polynomial and finds first DOY (274–365) where fitted VI ≤ threshold; assigns –999 for no detection.
- Exports yearly EOS_<year>_CONUS with NDVI_EOS and EVI_EOS bands.

4. 04_Clean_SOS_EOS.js (Masking SOS/EOS)

- Fetches MODIS land‑cover (MCD12Q1 LC_Type1) up to year of interest.
- Masks out Cropland/Urban/Mosaic/Barren (classes 12, 13, 14, 16).
- Masks invalid SOS/EOS values (0 and –999).

Reprojects to EPSG:4326 (0.0045° ≈ 500 m) and exports masked assets: EOS_<year>_CONUS_masked.

5. 05_Clean_POS_and_Length.js (Masking POS & Length)

- Applies same LC mask and invalid‐value mask to POS outputs.
- Computes POS length bands: NDVI_POSlen = POSend – POSstart + 1 (and for EVI).
- Exports POS_<year>_CONUS_masked with six bands.

6. 06_TheilSen_Slopes.js (Robust Trends)

- Builds per‐band image collections from annual phenology assets (Phenology_<year>_CONUS).
- Applies stable‐land‐cover mask (MCD12Q1 LC_Type5 unchanged 2001–2023).
- Calculates Theil–Sen slope and Kendall τ p‐value mask for each of the 10 bands.
- Exports a single 10‑band slope raster: GreeningTrends.

7. 07_Stack_Phenology.js (Final Stack)
   
- Aligns masked SOS, POS, and EOS rasters to a common grid.
- Stacks all 10 clean bands into Phenology_<year>_CONUS assets per year.


Outputs

-Phenology stacks: projects/horia-olariu/assets/Greening/Phenology_<year>_CONUS
-Trends raster: projects/horia-olariu/assets/Greening/GreeningTrends (10 bands of robust slopes)
-Input AOI: projects/horia-olariu/assets/Greening/CONUS_Union
