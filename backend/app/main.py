# backend/app/main.py

from fastapi import FastAPI # Import the main FastAPI class
from fastapi.middleware.cors import CORSMiddleware # Import CORS middleware for cross-origin requests

from app.api.v1 import metrics # Import our metrics API router
from app.config import settings # Import our application settings

# Initialize the FastAPI application.
# Provide metadata like title, description, and version for API documentation (Swagger UI).
app = FastAPI(
    title="Smart Incident Response Backend",
    description="API for monitoring, incident detection, and response for cloud infrastructure.",
    version="0.1.0",
)

# Configure CORS (Cross-Origin Resource Sharing) middleware.
# CORS is a security feature implemented by web browsers that restricts web pages
# from making requests to a different domain than the one that served the web page.
# Since our frontend (React) will likely be on a different domain/port than our backend (FastAPI),
# we need to explicitly allow requests from the frontend's origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, "*" allows all origins.
                          # IMPORTANT: In production, change this to a specific list of
                          # trusted frontend URLs (e.g., ["https://your-frontend-domain.com", "http://localhost:3000"]).
    allow_credentials=True, # Allow cookies and authentication headers to be sent with requests.
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.).
    allow_headers=["*"],  # Allow all HTTP headers in the request.
)

# Include our API routers into the main FastAPI application.
# - metrics.router: The APIRouter instance defined in app/api/v1/metrics.py.
# - prefix="/api/v1": All endpoints in this router will be prefixed with "/api/v1".
#   For example, the /metrics/cpu endpoint becomes /api/v1/metrics/cpu.
app.include_router(metrics.router, prefix="/api/v1")

# Define a simple root endpoint for a health check.
# This is useful to quickly verify if the API is running.
@app.get("/")
async def read_root():
    """
    Root endpoint for the Smart Incident Response Backend.
    Provides a welcome message and directs to API documentation.
    """
    return {"message": "Welcome to Smart Incident Response Backend! Visit /docs for API documentation."}

# How to run this application locally during development:
# From the 'backend/' directory, with your virtual environment activated:
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# The '--reload' flag automatically reloads the server when code changes are detected.
