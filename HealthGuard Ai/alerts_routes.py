# alerts_routes.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy.orm import Session
from database import get_db
from models import Alert

router = APIRouter()

# ---------- Pydantic Schemas ----------
class AlertCreate(BaseModel):
    city: str
    severity: str           # "info", "warning", "high"
    title: str
    detail: str
    expires_in_hours: Optional[int] = None  # if provided, we'll set expires

class AlertOut(BaseModel):
    id: int
    city: str
    severity: str
    title: str
    detail: str
    expires: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True


# ---------- Create Alert ----------
@router.post("/alerts", response_model=AlertOut)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    expires = None
    if alert.expires_in_hours is not None:
        expires = datetime.utcnow() + timedelta(hours=alert.expires_in_hours)

    new_alert = Alert(
        city=alert.city,
        severity=alert.severity,
        title=alert.title,
        detail=alert.detail,
        expires=expires,
        created_at=datetime.utcnow(),
        sent=False,
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert


# ---------- Get Active Alerts by City ----------
@router.get("/alerts/city", response_model=List[AlertOut])
def city_alerts(city: str = "Mumbai", db: Session = Depends(get_db)):
    now = datetime.utcnow()

    alerts = (
        db.query(Alert)
        .filter(Alert.city == city)
        .filter((Alert.expires.is_(None)) | (Alert.expires > now))
        .order_by(Alert.created_at.desc())
        .all()
    )

    return alerts
