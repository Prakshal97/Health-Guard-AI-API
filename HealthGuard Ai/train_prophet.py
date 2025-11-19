# train_prophet.py
import pandas as pd
from prophet import Prophet
import joblib
import warnings
warnings.filterwarnings("ignore")

print("Loading synthetic_patient_inflow.csv ...")
df = pd.read_csv("synthetic_patient_inflow.csv", parse_dates=['ds'])
print("Rows:", len(df))

m = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
print("Fitting Prophet model (may take 1-5 minutes depending on CPU)...")
m.fit(df)

joblib.dump(m, "prophet_patient_model.pkl")
print("Saved model: prophet_patient_model.pkl")
