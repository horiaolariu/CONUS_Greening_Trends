XGBoost + SHAP Analysis Pipeline

This Python script performs hyperparameter optimization, model evaluation, and SHAP-based feature importance analysis for multiple phenological slope metrics derived from environmental data.


Table of Contents

- Overview
- Prerequisites
- Script Workflow
- Results & Outputs
- File Structure


Overview

- Loads a CSV stack of environmental predictors and target slope metrics (SOS, POS, POE, EOS).
- Cleans the data (handles missing values, drops unwanted columns).
- Splits data into training and testing sets (stratified by ecoregion).
- Runs a randomized hyperparameter search over XGBoost regressors within a scikit-learn pipeline.
- Fits the final XGBoost model and evaluates performance metrics (RMSE, MAE, R², slope, intercept, MBE).
- Computes global SHAP feature importance and saves bar plots.
- Saves per-sample SHAP values as Parquet files.


Prerequisites

- Python 3.8+

Required libraries:

- numpy, pandas, matplotlib
- scikit-learn (v0.24+)
- xgboost
- shap
- tqdm

  
Script Workflow: XGBoost_SHAP_Hyper_opt.py

1. Data Loading & Cleaning
  
- Reads CSV into pandas, replaces -9999 with NaN.
- Drops index columns and non-target/NDVI/POS-length features.
- Model Loop for each target (SOS, POS, POE, EOS):
- Subset data, split into train/test (20% test, stratified).
- Define an XGBRegressor within a Pipeline that standardizes features.
- Define hyperparameter search space (e.g., n_estimators, max_depth, learning_rate).
- Execute RandomizedSearchCV (4-fold CV).
- Fit the final model with best parameters on training set.


2. Evaluation

Predict on test set and compute:

- RMSE, MAE, R²
- Linear fit slope & intercept between predictions and observations
- Mean Bias Error (MBE)
- Print metrics and best hyperparameters.

3. SHAP Analysis

- Scale test features with the pipeline’s scaler.
- Initialize shap.Explainer on the trained XGBoost model.
- Compute SHAP values for the test set.
- Generate and save a SHAP summary bar plot with metrics annotation.
- Save per-row SHAP values as Parquet (SHAP_values_{key}.parquet).

4. Completion

- Print final confirmation and output directory path.


Results & Outputs

All outputs are saved under the OUT directory:

- SHAP Plots: SHAP_values_EOS_PlusNames.png, SHAP_values_POS_PlusNames.png, etc.
- SHAP Values: SHAP_values_SOS.parquet, SHAP_values_POS.parquet, etc.
