# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import monitoring # CORRECTED: Import our monitoring router
from app.config import settings

app = FastAPI(
    title="Smart Incident Response Backend",
    description="API for monitoring, incident detection, and response for cloud infrastructure.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our API routers.
# The prefix "/api/v1" will apply to all endpoints in the monitoring router.
app.include_router(monitoring.router, prefix="/api/v1") # CORRECTED: Use monitoring.router

@app.get("/")
async def read_root():
    return {"message": "Welcome to Smart Incident Response Backend! Visit /docs for API documentation."}

