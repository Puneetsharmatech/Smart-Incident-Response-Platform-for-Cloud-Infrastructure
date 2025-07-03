# backend/app/api/v1/metrics.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

from app.services.azure_monitor_service import AzureMonitorService
from app.models.metric_data import MetricResponse

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
    responses={404: {"description": "Not found"}},
)

def get_azure_monitor_service():
    return AzureMonitorService()

@router.get("/cpu/{duration_minutes}", response_model=MetricResponse)
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

@router.get("/memory/{duration_minutes}", response_model=MetricResponse)
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

@router.get("/network/{duration_minutes}", response_model=MetricResponse)
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

