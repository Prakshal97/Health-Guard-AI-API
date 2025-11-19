# train_models.py
import os
import pandas as pd
from prophet import Prophet
import joblib
from sklearn.metrics import mean_absolute_error
import numpy as np

DATA = "synthetic_patient_inflow.csv"
OUTDIR = "models"
os.makedirs(OUTDIR, exist_ok=True)

df = pd.read_csv(DATA, parse_dates=["ds"])
cities = df["city"].unique()

results = {}
for city in cities:
    print("Training model for:", city)
    city_df = df[df.city == city].sort_values("ds").reset_index(drop=True)

    m = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
    # add regressors
    reg_cols = ["aqi","temp","humidity","flu_cases","dengue_cases","event","holiday"]
    for r in reg_cols:
        m.add_regressor(r)

    # train/val split (last 90 days validation)
    train = city_df.iloc[:-90]
    valid = city_df.iloc[-90:]

    # Prophet expects columns 'ds' and 'y'
    m.fit(train[["ds","y"] + reg_cols])

    # Save model
    p = os.path.join(OUTDIR, f"prophet_{city.lower()}.pkl")
    joblib.dump(m, p)
    print("Saved model to", p)

    # Validate: create future using regressor values from valid
    future = valid[["ds"] + reg_cols].copy()
    forecast = m.predict(future)
    # compute MAE
    mae = mean_absolute_error(valid["y"].values, forecast["yhat"].values)
    print(f"{city} validation MAE:", mae)
    results[city] = {"mae": float(mae)}

print("Done. Summary:", results)
