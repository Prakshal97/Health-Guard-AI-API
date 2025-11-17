from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class PollutionInput(BaseModel):
    pm25: float
    pm10: float

@router.post("/pollution-risk")
def pollution_risk(data: PollutionInput):
    pm25 = data.pm25
    pm10 = data.pm10

    score = 0

    if pm25 > 60:
        score += 2
    elif pm25 > 30:
        score += 1

    if pm10 > 100:
        score += 2
    elif pm10 > 50:
        score += 1

    if score <= 1:
        risk = "Low"
        advice = "Air quality is fine. No precautions needed."
    elif score == 2:
        risk = "Moderate"
        advice = "Sensitive groups should avoid outdoor exposure."
    else:
        risk = "High"
        advice = "Wear N95 mask and avoid going outdoors."

    return {
        "risk": risk,
        "advice": advice
    }
