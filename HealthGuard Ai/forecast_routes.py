# forecast_routes.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
import os

router = APIRouter()

# ---------------------------------------------------------------------
# 1. MULTI-CITY MODEL LOADING
# ---------------------------------------------------------------------
MODEL_DIR = "models"

CITY_MODELS = {
    "mumbai": os.path.join(MODEL_DIR, "prophet_mumbai.pkl"),
    "delhi": os.path.join(MODEL_DIR, "prophet_delhi.pkl"),
    "bengaluru": os.path.join(MODEL_DIR, "prophet_bengaluru.pkl"),
}

loaded_models = {}

for city_key, path in CITY_MODELS.items():
    if os.path.exists(path):
        try:
            loaded_models[city_key] = joblib.load(path)
            print(f"[✔] Loaded model for: {city_key}")
        except Exception as e:
            print(f"[x] Failed to load model for {city_key}: {e}")
    else:
        print(f"[!] Model file not found for {city_key}: {path}")

# ---------------------------------------------------------------------
# 2. SYNTHETIC MODE FALLBACK
# ---------------------------------------------------------------------
def generate_synthetic_forecast(start_date: datetime, days: int):
    dates = [start_date + timedelta(days=i) for i in range(days)]
    base = 250 + 40 * np.sin(np.linspace(0, 6.28, days))
    weekday_factor = [1.0 if d.weekday() < 5 else 0.85 for d in dates]
    noise = np.random.normal(0, 15, size=days)
    pollution = np.random.choice([0, 10, 20, 35], size=days, p=[0.6, 0.25, 0.1, 0.05])

    result = []

    for i, d in enumerate(dates):
        y = base[i] * weekday_factor[i] + noise[i] + pollution[i]
        y = round(y, 2)

        lower = max(0, y - np.random.uniform(10, 25))
        upper = y + np.random.uniform(10, 25)

        if pollution[i] >= 30:
            driver = "High pollution spike"
        elif pollution[i] >= 20:
            driver = "Moderate pollution"
        elif d.weekday() >= 5:
            driver = "Weekend effect"
        else:
            driver = "Baseline variation"

        result.append({
            "date": d.strftime("%Y-%m-%d"),
            "yhat": float(y),
            "yhat_lower": float(round(lower, 2)),
            "yhat_upper": float(round(upper, 2)),
            "drivers": driver
        })

    return result

# ---------------------------------------------------------------------
# 3. RESOURCE ESTIMATION MODULE
# ---------------------------------------------------------------------
def compute_resources(patients):
    staff = int(patients * 0.05)
    icu = int(patients * 0.08)
    oxygen = int(patients * 20)

    breakdown = {
        "staff": {
            "required": staff,
            "doctors": max(1, staff // 4),
            "nurses": max(1, staff // 2),
            "support": max(0, staff - (staff // 4) - (staff // 2)),
        },
        "icu": {
            "required": icu,
            "ventilator_beds": int(icu * 0.4),
            "non_ventilator_beds": icu - int(icu * 0.4),
        },
        "oxygen": {
            "total_l_per_day": oxygen,
            "cylinders_approx": int(oxygen / 6000),
        },
    }

    summary = {
        "staff_required": staff,
        "icu_required": icu,
        "oxygen_needed_l_per_day": oxygen,
    }

    return summary, breakdown

# ---------------------------------------------------------------------
# 4. MAIN FORECAST ROUTE
# ---------------------------------------------------------------------
@router.get("/forecast/patient-inflow-with-resources")
def forecast_with_resources(city: str = "Mumbai", days: int = 7, use_model: bool = True):
    start_date = datetime.utcnow()
    city_key = city.lower().strip()

    # ----------------------------
    #   USE REAL PROPHET MODEL
    # ----------------------------
    if use_model and city_key in loaded_models:
        model = loaded_models[city_key]
        future = model.make_future_dataframe(periods=days, freq="D")
        forecast = model.predict(future)
        last = forecast.tail(days)

        predictions = []
        for _, row in last.iterrows():
            predictions.append({
                "date": row["ds"].strftime("%Y-%m-%d"),
                "yhat": float(round(row["yhat"], 2)),
                "yhat_lower": float(round(row["yhat_lower"], 2)),
                "yhat_upper": float(round(row["yhat_upper"], 2)),
                "drivers": f"Prophet forecast ({city})",
            })

        source = f"prophet_model_{city_key}"

    else:
        # ----------------------------
        #   SYNTHETIC MODE
        # ----------------------------
        predictions = generate_synthetic_forecast(start_date, days)
        source = "simulated"

    # ----------------------------
    #   ADD RESOURCE ESTIMATIONS
    # ----------------------------
    results = []
    for p in predictions:
        patients = int(round(p["yhat"]))
        summary, breakdown = compute_resources(patients)

        results.append({
            "date": p["date"],
            "prediction": p,
            "resources": {
                "summary": summary,
                "breakdown": breakdown,
            },
        })

    return {
        "city": city,
        "model_source": source,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "results": results,
    }
