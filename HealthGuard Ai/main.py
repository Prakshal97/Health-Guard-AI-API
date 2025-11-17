# main.py
from fastapi import FastAPI

from pollution_data import get_pollution_data, get_daily_pollution_readings  # keep your existing
from pollution_risk import router as pollution_router
from resource_routes import router as resource_router
from hospital_routes import router as hospital_router
from forecast_routes import router as forecast_router
from aqi_routes import router as aqi_router
from events_routes import router as events_router
from alerts_routes import router as alerts_router

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
# mount the frontend folder at /app (so index at /app/)
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")


# include routers
app.include_router(pollution_router)
app.include_router(resource_router)
app.include_router(hospital_router)
app.include_router(forecast_router)
app.include_router(aqi_router)
app.include_router(events_router)
app.include_router(alerts_router)

@app.get("/")
def home():
    return {"message": "HealthGuard AI Backend Running"}
