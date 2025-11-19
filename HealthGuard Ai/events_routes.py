# events_routes.py
from fastapi import APIRouter
from datetime import date, timedelta

router = APIRouter()

# mock upcoming events
_mock_events = [
    {"name": "Diwali", "date": "2025-10-24", "expected_surge": "High", "impact": ["Trauma","Burns","Respiratory"], "notes": "Anticipate traffic and fireworks-related injuries"},
    {"name": "Holi", "date": "2026-03-25", "expected_surge": "Medium", "impact": ["Eye injury","Skin allergies"], "notes": "Color-related irritations expected"},
    {"name": "Ganesh Chaturthi", "date": "2025-09-12", "expected_surge": "Low", "impact": ["Drowning risk","Heat stroke"], "notes": "Crowd management advised"}
]

@router.get("/events/upcoming")
def upcoming_events(city: str = "Mumbai", days_ahead: int = 60):
    # For prototype return events whose date is within days_ahead from today OR full sample
    # Here we simply return the mock list for simplicity
    return {"city": city, "events": _mock_events}
