import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

cities = ["Mumbai", "Delhi", "Bengaluru"]
start_date = datetime(2020, 1, 1)
end_date = datetime(2025, 1, 1)

dates = pd.date_range(start=start_date, end=end_date, freq="D")

data = []

for city in cities:
    for ds in dates:
        base = {
            "Mumbai": 220,
            "Delhi": 250,
            "Bengaluru": 180
        }[city]

        month = ds.month
        season_factor = {
            1: 1.1, 2: 1.05, 3: 1.0,
            4: 0.95, 5: 0.9, 6: 1.1,
            7: 1.2, 8: 1.15, 9: 1.05,
            10: 1.1, 11: 1.2, 12: 1.3
        }[month]

        aqi = np.random.normal(120 if city == "Delhi" else 80, 20)
        temp = np.random.normal(30 if city != "Delhi" else 25, 4)
        humidity = np.random.normal(70, 15)

        flu_cases = max(0, np.random.poisson(30))
        dengue_cases = max(0, np.random.poisson(15 if month in [6,7,8,9] else 5))

        event = 1 if random.random() < 0.03 else 0
        holiday = 1 if ds.weekday() >= 5 else 0

        y = int(
            base * season_factor
            + flu_cases * 0.5
            + dengue_cases * 1.2
            + (aqi - 50) * 0.2
            + event * 40
            + holiday * 10
            + np.random.normal(0, 12)
        )

        data.append([
            city, ds, y, aqi, temp, humidity,
            flu_cases, dengue_cases, event, holiday
        ])

df = pd.DataFrame(data, columns=[
    "city", "ds", "y", "aqi", "temp", "humidity",
    "flu_cases", "dengue_cases", "event", "holiday"
])

df.to_csv("synthetic_patient_inflow.csv", index=False)
print("Dataset generated successfully with shape:", df.shape)
