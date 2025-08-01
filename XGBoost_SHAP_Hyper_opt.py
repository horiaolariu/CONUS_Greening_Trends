# Use the console tqdm to avoid the IProgress warning in Spyder
from tqdm import tqdm

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from scipy.stats import randint, uniform

import xgboost as xgb
import shap

# ------------------------------ paths -------------------------
CSV = Path(r"F:\Greening_study\randomSample_slopeStack\randomSampleStack.csv")
OUT = Path(r"F:\Greening_study\xgBoost_SHAP_results_hyperopt")
OUT.mkdir(parents=True, exist_ok=True)

# ------------------------ constants / helpers -----------------
RND    = 42
N_ITER = 200
UNITS  = "day yr⁻¹"

pretty = lambda s: s.replace("_", " ")

# -------------------- 1. load & clean data --------------------
df = pd.read_csv(CSV).replace(-9999, np.nan)
for drop in ("Unnamed: 0", "index"):
    if drop in df.columns:
        df.drop(columns=drop, inplace=True)

targets = {
    "SOS": "EVI_SOS_slope",
    "POS": "EVI_POSstart_slope",
    "POE": "EVI_POSend_slope",
    "EOS": "EVI_EOS_slope",
}

exclude = (
      ["ecoName", "lon", "lat"]
    + list(targets.values())
    + [c for c in df.columns if c.startswith("NDVI_")]
    + [c for c in df.columns if c.endswith("POSlen_slope")]
)

# -------------------- 2. loop over targets --------------------
for key, y_col in targets.items():
    sub = df.dropna(subset=[y_col]).copy()
    train_idx, test_idx = train_test_split(
        sub.index,
        test_size=0.20,
        random_state=RND,
        stratify=sub["ecoName"],
    )

    X = sub.drop(columns=exclude)
    X_train, X_test = X.loc[train_idx], X.loc[test_idx]
    y_train = sub.loc[train_idx, y_col]
    y_test  = sub.loc[test_idx,  y_col]

    # ----- hyperparameter search (no early stopping) -----
    base_model = xgb.XGBRegressor(
        objective="reg:squarederror",
        tree_method="hist",
        random_state=RND,
    )
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("xgb",    base_model),
    ])

    param_space = {
        "xgb__n_estimators":      randint(300, 1200),
        "xgb__max_depth":         randint(3, 12),
        "xgb__learning_rate":     uniform(loc=0.005, scale=0.045),
        "xgb__subsample":         uniform(loc=0.6, scale=0.4),
        "xgb__colsample_bytree":  uniform(loc=0.5, scale=0.4),
        "xgb__min_child_weight":  randint(1, 8),
        "xgb__gamma":             uniform(loc=0.0, scale=0.3),
    }

    search = RandomizedSearchCV(
        pipeline,
        param_space,
        n_iter=N_ITER,
        cv=4,
        n_jobs=-1,
        random_state=RND,
        scoring="neg_root_mean_squared_error",
    )
    search.fit(X_train, y_train)

    best_params = search.best_params_
    # strip off the "xgb__" prefix
    xgb_params = {k.split("__", 1)[1]: v for k, v in best_params.items()}

    # ----- final fit (no early stopping) -----
    final_model = xgb.XGBRegressor(
        objective="reg:squarederror",
        tree_method="hist",
        random_state=RND,
        eval_metric="rmse",
        **xgb_params,
    )
    final_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("xgb",    final_model),
    ])
    final_pipeline.fit(X_train, y_train)

    # -------------- compute metrics ----------------------------
    y_pred = final_pipeline.predict(X_test)
    mse  = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae  = mean_absolute_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)

    # slope + intercept
    lr = LinearRegression().fit(
        y_test.values.reshape(-1, 1),
        y_pred
    )
    slope, intercept = lr.coef_[0], lr.intercept_
    mbe = np.mean(y_pred - y_test)

    # bare prints for metrics and hyperparams
    print(f"{key} | RMSE={rmse:.4f}  MAE={mae:.4f}  R²={r2:.4f}  "
          f"Slope={slope:.4f}  Intercept={intercept:.4f}  MBE={mbe:.4f}")
    print(f"  Best XGB params → {xgb_params}")

    # -------------- SHAP on test set ----------------------------
    X_test_scaled = final_pipeline.named_steps["scaler"].transform(X_test)
    X_test_disp = pd.DataFrame(
        X_test_scaled,
        index=X_test.index,
        columns=[pretty(c) for c in X.columns]
    )

    explainer = shap.Explainer(
        final_pipeline.named_steps["xgb"],
        X_test_scaled
    )
    shap_values = explainer(X_test_scaled)

    plt.figure(figsize=(9, 7))
    shap.plots.bar(shap_values, show=False)
    plt.xlabel(f"Importance ({UNITS})", fontsize=12)
    plt.title(f"Global SHAP importance – {key}", fontsize=14)

    box_txt = (
        f"RMSE       : {rmse:.3f} {UNITS}\n"
        f"MAE        : {mae:.3f} {UNITS}\n"
        f"R²         : {r2:.3f}\n"
        f"Slope      : {slope:.3f}\n"
        f"Intercept  : {intercept:.3f}\n"
        f"MBE        : {mbe:.3f} {UNITS}"
    )
    plt.gcf().text(
        0.68, 0.85, box_txt,
        fontsize=11, ha="left", va="top",
        bbox=dict(facecolor="white", edgecolor="black",
                  alpha=0.9, pad=10.0)
    )
    plt.tight_layout()
    plt.savefig(OUT / f"SHAP_summary_{key}.png", dpi=300)
    plt.close()

    # per‑row SHAP values
    pd.DataFrame(
        shap_values.values,
        index=X_test.index,
        columns=X_test_disp.columns
    ).assign(rowID=X_test.index) \
     .to_parquet(OUT / f"SHAP_values_{key}.parquet", index=False)

print("✓ All done – outputs saved to:", OUT.resolve())

