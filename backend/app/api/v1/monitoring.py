# backend/app/api/v1/monitoring.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

from app.services.azure_monitor_service import AzureMonitorService
from app.services.incident_detection_service import IncidentDetectionService, Incident
from app.main import get_firestore_client, get_app_id

# We still need to import MetricResponse for type hinting within the functions,
# but FastAPI's response_model needs to be a string to avoid circular import issues at module load time.
from app.models.metric_data import MetricResponse # Keep this import for type hinting

router = APIRouter(
    tags=["Monitoring"],
    responses={404: {"description": "Not found"}},
)

def get_azure_monitor_service():
    return AzureMonitorService()

def get_incident_detection_service(
    db_client: Any = Depends(get_firestore_client),
    app_id: str = Depends(get_app_id)
):
    return IncidentDetectionService(db_client=db_client, app_id=app_id)

# --- Metric Endpoints ---
# FIX: Change response_model to a string literal
@router.get("/metrics/cpu/{duration_minutes}", response_model="app.models.metric_data.MetricResponse")
async def get_cpu_metrics(
    duration_minutes: int,
    azure_monitor_service: AzureMonitorService = Depends(get_azure_monitor_service)
) -> MetricResponse: # Add return type hint for clarity
    """
    Fetches CPU utilization metrics for the configured VM.
    """
    if duration_minutes <= 0:
        raise HTTPException(status_code=400, detail="Duration must be a positive integer.")
    metrics = await azure_monitor_service.get_vm_cpu_metrics(duration_minutes=duration_minutes)
    if not metrics.value:
        raise HTTPException(status_code=500, detail="Could not fetch CPU metrics. Check backend logs for errors.")
    return metrics

# FIX: Change response_model to a string literal
@router.get("/metrics/memory/{duration_minutes}", response_model="app.models.metric_data.MetricResponse")
async def get_memory_metrics(
    duration_minutes: int,
    azure_monitor_service: AzureMonitorService = Depends(get_azure_monitor_service)
) -> MetricResponse: # Add return type hint for clarity
    """
    Fetches Available Memory Bytes metrics for the configured VM.
    """
    if duration_minutes <= 0:
        raise HTTPException(status_code=400, detail="Duration must be a positive integer.")
    metrics = await azure_monitor_service.get_vm_memory_metrics(duration_minutes=duration_minutes)
    if not metrics.value:
        raise HTTPException(status_code=500, detail="Could not fetch Memory metrics. Check backend logs for errors.")
    return metrics

# FIX: Change response_model to a string literal
@router.get("/metrics/network/{duration_minutes}", response_model="app.models.metric_data.MetricResponse")
async def get_network_metrics(
    duration_minutes: int,
    azure_monitor_service: AzureMonitorService = Depends(get_azure_monitor_service)
) -> MetricResponse: # Add return type hint for clarity
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

# --- Incident Detection and Retrieval Endpoints ---
@router.get("/incidents/detect", response_model=List[Dict[str, Any]])
async def detect_incidents(
    azure_monitor_service: AzureMonitorService = Depends(get_azure_monitor_service),
    incident_detection_service: IncidentDetectionService = Depends(get_incident_detection_service)
):
    """
    Fetches latest metrics and runs incident detection rules.
    Returns a list of detected incidents and saves them to Firestore.
    """
    duration_for_detection = 10 # minutes

    cpu_metrics = await azure_monitor_service.get_vm_cpu_metrics(duration_minutes=duration_for_detection)
    memory_metrics = await azure_monitor_service.get_vm_memory_metrics(duration_minutes=duration_for_detection)
    network_metrics = await azure_monitor_service.get_vm_network_metrics(duration_minutes=duration_for_detection)

    detected_incidents = await incident_detection_service.run_detection(
        cpu_metrics,
        memory_metrics,
        network_metrics
    )

    return [inc.to_dict() for inc in detected_incidents]

@router.get("/incidents", response_model=List[Dict[str, Any]])
async def get_all_incidents(
    db_client: Any = Depends(get_firestore_client),
    app_id: str = Depends(get_app_id)
):
    """
    Retrieves all stored incidents from Firestore.
    """
    if not db_client or not app_id:
        raise HTTPException(status_code=500, detail="Firestore client or App ID not available.")

    try:
        incidents_collection_ref = db_client.collection(f"artifacts/{app_id}/public/data/incidents")
        
        docs = await incidents_collection_ref.get()
        
        all_incidents = []
        for doc in docs:
            incident_data = doc.to_dict()
            if incident_data:
                all_incidents.append(incident_data)
        
        all_incidents.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return all_incidents
    except Exception as e:
        print(f"Error fetching incidents from Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve incidents from database: {e}")

