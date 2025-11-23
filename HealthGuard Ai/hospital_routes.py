# hospital_routes.py
from fastapi import APIRouter
from typing import Optional
from fastapi import Depends
from dependencies import get_current_user
from models import User
router = APIRouter()

# For prototype we simulate some hospital inventory. Later you can connect real DB.
_sample_hospitals = {
    "H123": {
        "name": "City General Hospital",
        "staff": {"doctors":20, "nurses":60, "support":20},
        "icu": {"ventilator_beds":25, "non_ventilator_beds":95},
        "oxygen": {"cylinders":120, "plant_output_lpm":4800, "tanks_output_lpm":2700}
    },
    "H456": {
        "name": "Eastside Medical Center",
        "staff": {"doctors":10, "nurses":30, "support":10},
        "icu": {"ventilator_beds":10, "non_ventilator_beds":40},
        "oxygen": {"cylinders":50, "plant_output_lpm":2000, "tanks_output_lpm":1200}
    }
}

@router.get("/hospital/protected")
def hospital_secret(user: User = Depends(get_current_user)):
    return {"message": f"Hello {user.name}, you are authorized!"}

@router.get("/hospital/staff")
def hospital_staff(
    hospital_id: Optional[str] = "H123",
    current_user: User = Depends(get_current_user)   # ⬅️ protect with JWT
):
    data = _sample_hospitals.get(hospital_id)
    if not data:
        return {"error": "hospital not found"}
    total_required = (
        data['staff']['doctors']
        + data['staff']['nurses']
        + data['staff']['support']
    )
    available = total_required
    deficit = max(0, total_required - available)
    return {
        "hospital_id": hospital_id,
        "name": data["name"],
        "total_required": total_required,
        "available": available,
        "deficit": deficit,
        "breakdown": data['staff'],
        "requested_by": current_user.email,   # just to see it works
    }
@router.get("/hospital/icu")
def hospital_icu(hospital_id: Optional[str] = "H123"):
    data = _sample_hospitals.get(hospital_id)
    if not data:
        return {"error": "hospital not found"}
    total_beds = data['icu']['ventilator_beds'] + data['icu']['non_ventilator_beds']
    available = total_beds
    deficit = max(0, total_beds - available)
    return {
        "hospital_id": hospital_id,
        "name": data["name"],
        "total_beds": total_beds,
        "available_beds": available,
        "deficit": deficit,
        "breakdown": data['icu']
    }

@router.get("/hospital/oxygen")
def hospital_oxygen(hospital_id: Optional[str] = "H123"):
    data = _sample_hospitals.get(hospital_id)
    if not data:
        return {"error": "hospital not found"}
    total_capacity = data['oxygen']['plant_output_lpm'] + data['oxygen']['tanks_output_lpm']
    current_usage = int(total_capacity * 0.9)  # sample
    deficit = max(0, total_capacity - current_usage)
    return {
        "hospital_id": hospital_id,
        "name": data["name"],
        "total_capacity_lpm": total_capacity,
        "current_usage_lpm": current_usage,
        "deficit_lpm": deficit,
        "breakdown": data['oxygen']
    }
