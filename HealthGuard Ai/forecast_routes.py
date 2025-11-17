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

# Try to load Prophet model if exists
MODEL_PATH = "prophet_patient_model.pkl"
_model = None
_model_source = "simulated"
try:
    if os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)
        _model_source = "prophet_model"
except Exception as e:
    print("Warning: Prophet model load failed:", e)
    _model = None
    _model_source = "simulated"

# Generate synthetic data if model unavailable
def generate_synthetic_forecast(start_date: datetime, days: int):
    dates = [start_date + timedelta(days=i) for i in range(days)]

    base = 250 + 40 * np.sin(np.linspace(0, 6.28, days))     # base trend
    weekday_factor = [1.0 if d.weekday() < 5 else 0.85 for d in dates]
    noise = np.random.normal(0, 15, size=days)
    pollution = np.random.choice([0, 10, 20, 35], size=days, p=[0.6, 0.25, 0.1, 0.05])

    final_values = (base * weekday_factor) + noise + pollution

    result = []
    for i, d in enumerate(dates):
        y = round(final_values[i], 2)
        lower = max(0, y - np.random.uniform(10, 25))
        upper = y + np.random.uniform(10, 25)

        if pollution[i] >= 30:
            driver = "High pollution spike"
        elif pollution[i] >= 20:
            driver = "Moderate pollution effect"
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

# Resource estimation logic
def compute_resources(patients):
    staff = int(patients * 0.05)
    icu = int(patients * 0.08)
    oxygen = int(patients * 20)

    breakdown = {
        "staff": {
            "required": staff,
            "doctors": max(1, staff // 4),
            "nurses": max(1, staff // 2),
            "support": max(0, staff - (staff // 4) - (staff // 2))
        },
        "icu": {
            "required": icu,
            "ventilator_beds": int(icu * 0.4),
            "non_ventilator_beds": icu - int(icu * 0.4)
        },
        "oxygen": {
            "total_l_per_day": oxygen,
            "cylinders_approx": int(oxygen / 6000)
        }
    }

    summary = {
        "staff_required": staff,
        "icu_required": icu,
        "oxygen_needed_l_per_day": oxygen
    }

    return summary, breakdown


@router.get("/forecast/patient-inflow-with-resources")
def forecast_with_resources(city: str = "Mumbai", days: int = 7, use_model: bool = True):
    start_date = datetime.utcnow()

    # If Prophet available & enabled
    if _model is not None and use_model:
        future = _model.make_future_dataframe(periods=days, freq='D')
        forecast = _model.predict(future)
        last = forecast.tail(days)

        predictions = []
        for _, row in last.iterrows():
            predictions.append({
                "date": row['ds'].strftime("%Y-%m-%d"),
                "yhat": float(round(row['yhat'], 2)),
                "yhat_lower": float(round(row['yhat_lower'], 2)),
                "yhat_upper": float(round(row['yhat_upper'], 2)),
                "drivers": "Model-based forecast"
            })

        source = "prophet_model"

    else:
        # fallback synthetic mode
        predictions = generate_synthetic_forecast(start_date, days)
        source = "simulated"

    # Attach resources for each day
    results = []
    for p in predictions:
        y = int(round(p["yhat"]))
        summary, breakdown = compute_resources(y)

        results.append({
            "date": p["date"],
            "prediction": p,
            "resources": {
                "summary": summary,
                "breakdown": breakdown
            }
        })

    return {
        "city": city,
        "model_source": source,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "results": results
    }
