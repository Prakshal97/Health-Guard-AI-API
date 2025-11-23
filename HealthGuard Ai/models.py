from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Boolean

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="citizen")  # citizen, hospital_admin, govt_officer
    created_at = Column(DateTime, default=datetime.utcnow)

    hospitals = relationship("Hospital", back_populates="admin")

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    city = Column(String(100), nullable=False)
    capacity_beds = Column(Integer, default=0)
    capacity_staff = Column(Integer, default=0)
    oxygen_capacity_lpm = Column(Integer, default=0)
    admin_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    admin = relationship("User", back_populates="hospitals")



# ^ make sure JSON, Float, Boolean are imported

# ... User + Hospital classes stay as they are ...


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), index=True)
    date = Column(DateTime, index=True)
    predicted_patients = Column(Float)
    model_source = Column(String(100))      # e.g. prophet_model_mumbai, simulated
    resources = Column(JSON)               # summary + breakdown dict
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), index=True)
    severity = Column(String(20))          # info / warning / high
    title = Column(String(200))
    detail = Column(String(500))
    expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent = Column(Boolean, default=False)
