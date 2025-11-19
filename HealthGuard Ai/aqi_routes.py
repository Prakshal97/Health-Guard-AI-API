# aqi_routes.py
from fastapi import APIRouter
from datetime import datetime, timedelta
import random

router = APIRouter()

def make_hourly_aqi(city: str, hours: int):
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    series = []
    base = 80 + (hash(city) % 20)  # slight city variation
    for i in range(hours):
        ts = now + timedelta(hours=i)
        # synthetic AQI with small noise and possible spikes
        aqi = int(max(10, base + 15 * (0.5 - random.random()) + (5 if random.random() < 0.1 else 0)))
        series.append({"ts": ts.isoformat() + "Z", "aqi": aqi})
    return series

@router.get("/pollution/aqi-trend")
def aqi_trend(city: str = "Mumbai", hours: int = 24):
    series = make_hourly_aqi(city, hours)
    legend = {"good": 50, "moderate": 100, "unhealthy": 150}
    return {"city": city, "hours": hours, "series": series, "legend": legend}
