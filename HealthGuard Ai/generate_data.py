# generate_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_patient_inflow(start='2023-01-01', days=730, seed=42):
    np.random.seed(seed)
    dates = pd.date_range(start=start, periods=days, freq='D')
    base = 200 + 40 * np.sin(np.linspace(0, 6.28*2, days))  # seasonal
    weekday_factor = np.array([1.0 if d.weekday() < 5 else 0.85 for d in dates])
    noise = np.random.normal(0, 15, size=days)
    pollution_effect = 10 * np.sin(np.linspace(0, 12.56, days))
    values = (base * weekday_factor) + noise + pollution_effect
    df = pd.DataFrame({'ds': dates, 'y': values.round().astype(int)})
    return df

if __name__ == "__main__":
    print("Generating synthetic patient inflow CSV...")
    df = generate_patient_inflow()
    df.to_csv("synthetic_patient_inflow.csv", index=False)
    print("Saved synthetic_patient_inflow.csv, rows =", len(df))
