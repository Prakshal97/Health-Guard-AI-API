# dashboard_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List

from database import get_db
from models import Forecast, Alert
from hospital_routes import _sample_hospitals  # reuse your mock data

router = APIRouter()


@router.get("/dashboard/summary")
def dashboard_summary(
    city: str = "Mumbai",
    hospital_id: Optional[str] = "H123",
    days: int = 7,
    db: Session = Depends(get_db),
):
    today = datetime.utcnow().date()
    end_date = today + timedelta(days=days)

    # 1) Upcoming forecasts for this city
    forecasts = (
        db.query(Forecast)
        .filter(Forecast.city == city)
        .filter(Forecast.date >= today)
        .filter(Forecast.date < end_date)
        .order_by(Forecast.date.asc())
        .all()
    )

    forecast_list = []
    patients_values = []

    for f in forecasts:
        d = f.date.date().isoformat()
        patients = float(f.predicted_patients)
        patients_values.append(patients)

        forecast_list.append(
            {
                "date": d,
                "predicted_patients": patients,
                "resources": f.resources,      # summary + breakdown
            }
        )

    # small safety
    if not patients_values:
        patients_values = [0]

    avg_patients = sum(patients_values) / len(patients_values)
    max_patients = max(patients_values)

    # 2) Active alerts for this city
    now = datetime.utcnow()
    alerts = (
        db.query(Alert)
        .filter(Alert.city == city)
        .filter((Alert.expires.is_(None)) | (Alert.expires > now))
        .order_by(Alert.created_at.desc())
        .all()
    )

    alerts_list = [
        {
            "id": a.id,
            "severity": a.severity,
            "title": a.title,
            "detail": a.detail,
            "created_at": a.created_at.isoformat(),
            "expires": a.expires.isoformat() if a.expires else None,
        }
        for a in alerts
    ]

    # 3) Hospital snapshot from mock dictionary
    hospital_info = _sample_hospitals.get(hospital_id)
    hospital_summary = None
    if hospital_info:
        total_staff = (
            hospital_info["staff"]["doctors"]
            + hospital_info["staff"]["nurses"]
            + hospital_info["staff"]["support"]
        )
        total_icu = (
            hospital_info["icu"]["ventilator_beds"]
            + hospital_info["icu"]["non_ventilator_beds"]
        )
        total_oxygen = (
            hospital_info["oxygen"]["plant_output_lpm"]
            + hospital_info["oxygen"]["tanks_output_lpm"]
        )
        hospital_summary = {
            "hospital_id": hospital_id,
            "name": hospital_info["name"],
            "total_staff": total_staff,
            "total_icu_beds": total_icu,
            "total_oxygen_lpm": total_oxygen,
            "raw": hospital_info,
        }

    return {
        "city": city,
        "hospital": hospital_summary,
        "forecast_horizon_days": days,
        "stats": {
            "avg_predicted_patients": round(avg_patients, 2),
            "max_predicted_patients": round(max_patients, 2),
            "total_alerts": len(alerts_list),
        },
        "forecasts": forecast_list,
        "alerts": alerts_list,
    }
