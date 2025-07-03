# backend/app/api/v1/metrics.py

from fastapi import APIRouter, HTTPException, Depends # Import necessary FastAPI components
from typing import List, Dict, Any # For type hinting

from app.services.azure_monitor_service import AzureMonitorService # Import our Azure Monitor service
from app.models.metric_data import MetricResponse # Import our Pydantic response model

# Create an API router. This helps organize endpoints into logical groups.
# - prefix: All endpoints defined in this router will start with "/metrics".
# - tags: Used for grouping endpoints in the OpenAPI (Swagger UI) documentation.
# - responses: Defines common responses for endpoints in this router (e.g., 404 Not Found).
router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
    responses={404: {"description": "Not found"}},
)

# Dependency function to provide an instance of AzureMonitorService.
# FastAPI's Dependency Injection system will call this function and
# inject its return value into the endpoint function.
def get_azure_monitor_service():
    """
    Returns an instance of AzureMonitorService.
    This allows for easy testing and management of the service dependency.
    """
    return AzureMonitorService()

# Define the API endpoint for fetching CPU metrics.
# - @router.get("/cpu/{duration_minutes}"): Defines a GET request endpoint.
#   - "/cpu/{duration_minutes}" specifies the path. `{duration_minutes}` is a path parameter.
# - response_model=MetricResponse: Tells FastAPI that the response from this endpoint
#   will conform to the MetricResponse Pydantic model, enabling automatic serialization
#   and OpenAPI documentation.
@router.get("/cpu/{duration_minutes}", response_model=MetricResponse)
async def get_cpu_metrics(
    duration_minutes: int, # FastAPI automatically converts the path parameter to an integer.
    # Use Depends to inject an instance of AzureMonitorService.
    azure_monitor_service: AzureMonitorService = Depends(get_azure_monitor_service)
):
    """
    Fetches CPU utilization metrics for the configured Azure VM.

    Args:
        duration_minutes: The duration in minutes for which to fetch CPU data (e.g., 5, 60).

    Returns:
        A MetricResponse object containing the CPU metrics.

    Raises:
        HTTPException:
            - 400 Bad Request if duration_minutes is not positive.
            - 500 Internal Server Error if metrics cannot be fetched from Azure Monitor.
    """
    # Input validation: Ensure duration_minutes is a valid positive integer.
    if duration_minutes <= 0:
        raise HTTPException(status_code=400, detail="Duration must be a positive integer.")

    # Call the Azure Monitor service to fetch CPU metrics.
    metrics = await azure_monitor_service.get_vm_cpu_metrics(duration_minutes=duration_minutes)

    # Check if any metrics were returned. If not, raise an HTTP 500 error.
    # The service itself handles internal errors by returning an empty MetricResponse.
    if not metrics.value:
        raise HTTPException(status_code=500, detail="Could not fetch CPU metrics. Check backend logs for errors.")

    # Return the fetched metrics. FastAPI will automatically serialize this Pydantic object to JSON.
    return metrics

