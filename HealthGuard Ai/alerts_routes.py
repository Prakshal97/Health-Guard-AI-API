# alerts_routes.py
from fastapi import APIRouter
from datetime import datetime, timedelta

router = APIRouter()

# mock advisories
_mock_alerts = [
    {"severity": "high", "title": "Major festival in 3 days", "detail": "Expect +35% surge in trauma & respiratory cases. Staff augmentation required.", "expires": None},
    {"severity": "warning", "title": "High humidity & stagnant water", "detail": "Vector control advised - dengue risk rising.", "expires": None},
    {"severity": "info", "title": "AQI improving over next 48 hours", "detail": "Monitor for waterborne diseases after rains.", "expires": None}
]

@router.get("/alerts/city")
def city_alerts(city: str = "Mumbai"):
    # In real system filter by city and timestamp; here return mock
    return {"city": city, "advisories": _mock_alerts}
