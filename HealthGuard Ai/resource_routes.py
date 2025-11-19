# resource_routes.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ResourceRequest(BaseModel):
    city: str = "Mumbai"
    date: Optional[str] = None  # YYYY-MM-DD
    predicted_patients: int

class BatchRequest(BaseModel):
    city: str = "Mumbai"
    items: List[ResourceRequest]

def estimate_for(p: int):
    staff_per_patient = 0.05        # 5 staff per 100 patients
    icu_ratio = 0.08
    oxygen_l_per_patient_per_day = 20

    staff_required = int(round(p * staff_per_patient))
    icu_required = int(round(p * icu_ratio))
    oxygen_needed_l = int(round(p * oxygen_l_per_patient_per_day))

    breakdown = {
        "staff": {
            "required": staff_required,
            "doctors": max(1, staff_required // 4),
            "nurses": max(1, staff_required // 2),
            "support": max(0, staff_required - (staff_required // 4) - (staff_required // 2))
        },
        "icu": {
            "required": icu_required,
            "ventilator_beds": int(round(icu_required * 0.4)),
            "non_ventilator_beds": icu_required - int(round(icu_required * 0.4))
        },
        "oxygen": {
            "total_l_per_day": oxygen_needed_l,
            "cylinders_approx": int(round(oxygen_needed_l / 6000))
        }
    }
    summary = {
        "staff_required": staff_required,
        "icu_required": icu_required,
        "oxygen_needed_l_per_day": oxygen_needed_l
    }
    return summary, breakdown

@router.post("/forecast/resources")
def estimate_resources(req: ResourceRequest):
    summary, breakdown = estimate_for(req.predicted_patients)
    return {
        "city": req.city,
        "date": req.date,
        "predicted_patients": req.predicted_patients,
        "summary": summary,
        "breakdown": breakdown
    }

@router.post("/forecast/resources/batch")
def batch_resources(req: BatchRequest):
    out = []
    for item in req.items:
        summary, breakdown = estimate_for(item.predicted_patients)
        out.append({
            "city": item.city,
            "date": item.date,
            "predicted_patients": item.predicted_patients,
            "summary": summary,
            "breakdown": breakdown
        })
    return {"results": out}
