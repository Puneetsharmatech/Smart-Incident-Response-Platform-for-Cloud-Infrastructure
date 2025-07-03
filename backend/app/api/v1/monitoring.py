# backend/app/api/v1/monitoring.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

from app.services.azure_monitor_service import AzureMonitorService
from app.services.incident_detection_service import IncidentDetectionService, Incident # Import the new service and Incident model
from app.models.metric_data import MetricResponse

# Create an API router. Note: The prefix will be included in app.main.py
router = APIRouter(
    tags=["Monitoring"], # Changed tag to be more general
    responses={404: {"description": "Not found"}},
)

# Dependency to get an instance of AzureMonitorService
def get_azure_monitor_service():
    return AzureMonitorService()

# Dependency to get an instance of IncidentDetectionService
def get_incident_detection_service():
    return IncidentDetectionService()

# --- Metric Endpoints (unchanged) ---
@router.get("/metrics/cpu/{duration_minutes}", response_model=MetricResponse)
async def get_cpu_metrics(
    duration_minutes: int,
    azure_monitor_service: AzureMonitorService = Depends(get_azure_monitor_service)
):
    """
    Fetches CPU utilization metrics for the configured VM.
    """
    if duration_minutes <= 0:
        raise HTTPException(status_code=400, detail="Duration must be a positive integer.")
    metrics = await azure_monitor_service.get_vm_cpu_metrics(duration_minutes=duration_minutes)
    if not metrics.value:
        raise HTTPException(status_code=500, detail="Could not fetch CPU metrics. Check backend logs for errors.")
    return metrics

@router.get("/metrics/memory/{duration_minutes}", response_model=MetricResponse)
async def get_memory_metrics(
    duration_minutes: int,
    azure_monitor_service: AzureMonitorService = Depends(get_azure_monitor_service)
):
    """
    Fetches Available Memory Bytes metrics for the configured VM.
    """
    if duration_minutes <= 0:
        raise HTTPException(status_code=400, detail="Duration must be a positive integer.")
    metrics = await azure_monitor_service.get_vm_memory_metrics(duration_minutes=duration_minutes)
    if not metrics.value:
        raise HTTPException(status_code=500, detail="Could not fetch Memory metrics. Check backend logs for errors.")
    return metrics

@router.get("/metrics/network/{duration_minutes}", response_model=MetricResponse)
async def get_network_metrics(
    duration_minutes: int,
    azure_monitor_service: AzureMonitorService = Depends(get_azure_monitor_service)
):
    """
    Fetches Network In Total and Network Out Total metrics for the configured VM.
    """
    if duration_minutes <= 0:
        raise HTTPException(status_code=400, detail="Duration must be a positive integer.")
    metrics = await azure_monitor_service.get_vm_network_metrics(duration_minutes=duration_minutes)
    if not metrics.value:
        raise HTTPException(status_code=500, detail="Could not fetch Network metrics. Check backend logs for errors.")
    return metrics
# --- End Metric Endpoints ---

# --- Incident Detection Endpoint ---
@router.get("/incidents/detect", response_model=List[Dict[str, Any]]) # Return a list of dictionaries for now
async def detect_incidents(
    azure_monitor_service: AzureMonitorService = Depends(get_azure_monitor_service),
    incident_detection_service: IncidentDetectionService = Depends(get_incident_detection_service)
):
    """
    Fetches latest metrics and runs incident detection rules.
    Returns a list of detected incidents.
    """
    # Fetch all necessary metrics for detection (e.g., last 10 minutes)
    # The duration here should be sufficient for the detection rules to analyze.
    duration_for_detection = 10 # minutes

    cpu_metrics = await azure_monitor_service.get_vm_cpu_metrics(duration_minutes=duration_for_detection)
    memory_metrics = await azure_monitor_service.get_vm_memory_metrics(duration_minutes=duration_for_detection)
    network_metrics = await azure_monitor_service.get_vm_network_metrics(duration_minutes=duration_for_detection)

    # Run detection logic
    detected_incidents = await incident_detection_service.run_detection(
        cpu_metrics,
        memory_metrics,
        network_metrics
    )

    # Convert Incident objects to dictionaries for JSON response
    return [inc.to_dict() for inc in detected_incidents]

