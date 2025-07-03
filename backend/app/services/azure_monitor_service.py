# backend/app/services/azure_monitor_service.py

from azure.identity import DefaultAzureCredential # Used for authenticating with Azure services
from azure.monitor.query import MetricsQueryClient, MetricAggregationType # Client for querying Azure Monitor metrics
from datetime import datetime, timedelta # For handling time ranges for metric queries
from typing import List, Dict, Any # For type hinting complex data structures

from app.config import settings # Import our application settings
from app.models.metric_data import MetricResponse, Metric, MetricTimeSeriesElement, MetricValue # Import our Pydantic data models

class AzureMonitorService:
    """
    Service class to interact with Azure Monitor for fetching metrics.
    """
    def __init__(self):
        # Initialize DefaultAzureCredential.
        # This credential provider automatically attempts to authenticate using various methods:
        # environment variables, Managed Identity (on Azure VM), Azure CLI, etc.
        # On our VM, it will seamlessly use the System-Assigned Managed Identity.
        self.credential = DefaultAzureCredential()
        # Initialize the MetricsQueryClient with the authenticated credential.
        self.metrics_client = MetricsQueryClient(credential=self.credential)

        # Retrieve Azure configuration details from our settings.
        self.subscription_id = settings.AZURE_SUBSCRIPTION_ID
        self.resource_group_name = settings.AZURE_RESOURCE_GROUP_NAME
        self.vm_name = settings.AZURE_VM_NAME

    async def get_vm_cpu_metrics(self, duration_minutes: int = 60) -> MetricResponse:
        """
        Fetches CPU utilization metrics for the specified VM from Azure Monitor.

        Args:
            duration_minutes: The duration in minutes for which to fetch metrics (e.g., 60 for the last hour).

        Returns:
            A MetricResponse object containing CPU utilization data, formatted according to our Pydantic models.
            Returns an empty MetricResponse if an error occurs or no metrics are found.
        """
        try:
            # Construct the full Azure Resource ID for the Virtual Machine.
            # This ID uniquely identifies the VM within your Azure subscription.
            # Format: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}
            resource_id = (
                f"/subscriptions/{self.subscription_id}/resourceGroups/"
                f"{self.resource_group_name}/providers/Microsoft.Compute/virtualMachines/"
                f"{self.vm_name}"
            )
            print(f"Fetching CPU metrics for resource ID: {resource_id}") # For debugging

            # Define the time range for the metric query.
            # We want data from 'now' minus 'duration_minutes' up to 'now' (UTC).
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=duration_minutes)

            # Query Azure Monitor for the 'Percentage CPU' metric.
            # - metric_names: The specific metric we are interested in.
            # - timespan: The start and end time for the query.
            # - granularity: The time interval for each data point (e.g., 1 minute).
            # - aggregations: The type of aggregation to apply (e.g., AVERAGE, TOTAL, MAXIMUM).
            response = self.metrics_client.query_resource(
                resource_id=resource_id,
                metric_names=["Percentage CPU"],
                timespan=(start_time, end_time),
                granularity=timedelta(minutes=1), # Fetch data points every 1 minute
                aggregations=[MetricAggregationType.AVERAGE] # Get the average CPU usage for each minute
            )

            # Process the raw response from Azure Monitor into our custom Pydantic models.
            metrics_list: List[Metric] = []
            for metric in response.metrics:
                timeseries_elements: List[MetricTimeSeriesElement] = []
                for ts in metric.timeseries:
                    data_values: List[MetricValue] = []
                    for data_point in ts.data:
                        # Create a MetricValue object for each data point.
                        # Note: Azure SDK's data_point attributes might be None if not aggregated.
                        data_values.append(MetricValue(
                            timeStamp=data_point.timestamp,
                            average=data_point.average,
                            count=data_point.count,
                            maximum=data_point.maximum,
                            minimum=data_point.minimum,
                            total=data_point.total
                        ))
                    # Create a MetricTimeSeriesElement for the current time series.
                    timeseries_elements.append(MetricTimeSeriesElement(data=data_values))

                # Create a Metric object for the current metric.
                metrics_list.append(Metric(
                    id=metric.id,
                    name=metric.name.value, # 'name' is an object, we need its 'value' attribute
                    type=metric.type,
                    unit=str(metric.unit), # 'unit' is an enum, convert to string
                    timeseries=timeseries_elements,
                    resourceId=resource_id # Store the full resource ID for context
                ))

            # Return the final MetricResponse containing all processed metrics.
            return MetricResponse(value=metrics_list)

        except Exception as e:
            # Catch any exceptions during the process (e.g., network issues, permission errors).
            # Print the error for debugging. In a production system, you'd use a proper logging framework.
            print(f"Error fetching CPU metrics: {e}")
            # Return an empty MetricResponse to indicate failure without crashing the API.
            return MetricResponse(value=[])

# This 'main' function is for local testing of the service in isolation, not part of the FastAPI app flow.
# To run this, uncomment the lines below and execute this file directly (e.g., `python -m asyncio azure_monitor_service.py`).
# import asyncio
# async def test_service():
#     service = AzureMonitorService()
#     cpu_metrics = await service.get_vm_cpu_metrics(duration_minutes=5)
#     if cpu_metrics.value:
#         print(f"Successfully fetched {len(cpu_metrics.value[0].timeseries[0].data)} CPU data points.")
#         # print(cpu_metrics.json(indent=2)) # Uncomment to see full JSON output
#     else:
#         print("Failed to fetch CPU metrics.")

# if __name__ == "__main__":
#     asyncio.run(test_service())
