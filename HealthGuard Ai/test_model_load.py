# test_model_load.py
import joblib
m = joblib.load("prophet_patient_model.pkl")
print("Model loaded. Make future DF and predict one day sample.")
import pandas as pd
future = m.make_future_dataframe(periods=3, freq='D')
pred = m.predict(future.tail(3))
print(pred[['ds','yhat','yhat_lower','yhat_upper']])
