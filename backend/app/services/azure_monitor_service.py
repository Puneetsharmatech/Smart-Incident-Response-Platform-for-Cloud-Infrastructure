# backend/app/services/azure_monitor_service.py

from azure.identity import DefaultAzureCredential
from azure.monitor.query import MetricsQueryClient, MetricAggregationType
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional # Ensure Optional is imported

from app.config import settings
from app.models.metric_data import MetricResponse, Metric, MetricTimeSeriesElement, MetricValue

class AzureMonitorService:
    """
    Service class to interact with Azure Monitor for fetching metrics.
    """
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.metrics_client = MetricsQueryClient(credential=self.credential)

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
            resource_uri = (
                f"/subscriptions/{self.subscription_id}/resourceGroups/"
                f"{self.resource_group_name}/providers/Microsoft.Compute/virtualMachines/"
                f"{self.vm_name}"
            )
            print(f"Fetching CPU metrics for resource ID: {resource_uri}")

            # Define the time range for the metric query.
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=duration_minutes)

            response = self.metrics_client.query_resource(
                resource_uri=resource_uri,
                metric_names=["Percentage CPU"],
                timespan=(start_time, end_time),
                granularity=timedelta(minutes=1),
                aggregations=[MetricAggregationType.AVERAGE]
            )

            metrics_list: List[Metric] = []
            for metric in response.metrics:
                timeseries_elements: List[MetricTimeSeriesElement] = []
                for ts in metric.timeseries:
                    data_values: List[MetricValue] = []
                    for data_point in ts.data:
                        data_values.append(MetricValue(
                            timeStamp=data_point.timestamp,
                            average=data_point.average,
                            count=data_point.count,
                            maximum=data_point.maximum,
                            minimum=data_point.minimum,
                            total=data_point.total
                        ))
                    timeseries_elements.append(MetricTimeSeriesElement(data=data_values))

                # --- FIX STARTS HERE ---
                # Check if metric.name is an object with a 'value' attribute or a direct string/dict
                metric_name_value = metric.name.value if hasattr(metric.name, 'value') else metric.name
                # Ensure metric_name_value is a dictionary as expected by our Pydantic model
                if not isinstance(metric_name_value, dict):
                    metric_name_value = {"value": str(metric_name_value), "localizedValue": str(metric_name_value)}

                # Check if metric.unit is an enum with a 'value' attribute or a direct string
                metric_unit_value = str(metric.unit.value) if hasattr(metric.unit, 'value') else str(metric.unit)
                # --- FIX ENDS HERE ---

                metrics_list.append(Metric(
                    id=metric.id,
                    name=metric_name_value, # Use the corrected name value
                    type=metric.type,
                    unit=metric_unit_value, # Use the corrected unit value
                    timeseries=timeseries_elements,
                    resourceId=resource_uri
                ))

            return MetricResponse(value=metrics_list)

        except Exception as e:
            print(f"Error fetching CPU metrics: {e}")
            return MetricResponse(value=[])
