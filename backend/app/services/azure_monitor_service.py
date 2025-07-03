# backend/app/services/azure_monitor_service.py

from azure.identity import DefaultAzureCredential
from azure.monitor.query import MetricsQueryClient, MetricAggregationType
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

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

    # Helper method to construct resource ID (reused by all metric methods)
    def _get_vm_resource_uri(self) -> str:
        """Constructs the full Azure Resource ID for the configured VM."""
        return (
            f"/subscriptions/{self.subscription_id}/resourceGroups/"
            f"{self.resource_group_name}/providers/Microsoft.Compute/virtualMachines/"
            f"{self.vm_name}"
        )

    # Helper method to process raw Azure Monitor response into our Pydantic models
    def _process_metric_response(self, response: Any, resource_uri: str) -> MetricResponse:
        """Processes raw Azure Monitor response into MetricResponse Pydantic model."""
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

            metric_name_value = metric.name.value if hasattr(metric.name, 'value') else metric.name
            if not isinstance(metric_name_value, dict):
                metric_name_value = {"value": str(metric_name_value), "localizedValue": str(metric_name_value)}

            metric_unit_value = str(metric.unit.value) if hasattr(metric.unit, 'value') else str(metric.unit)

            metrics_list.append(Metric(
                id=metric.id,
                name=metric_name_value,
                type=metric.type,
                unit=metric_unit_value,
                timeseries=timeseries_elements,
                resourceId=resource_uri
            ))
        return MetricResponse(value=metrics_list)

    async def get_vm_cpu_metrics(self, duration_minutes: int = 60) -> MetricResponse:
        """
        Fetches CPU utilization metrics for the configured VM from Azure Monitor.
        """
        try:
            resource_uri = self._get_vm_resource_uri()
            print(f"Fetching CPU metrics for resource ID: {resource_uri}")

            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=duration_minutes)

            response = self.metrics_client.query_resource(
                resource_uri=resource_uri,
                metric_names=["Percentage CPU"],
                timespan=(start_time, end_time),
                granularity=timedelta(minutes=1),
                aggregations=[MetricAggregationType.AVERAGE]
            )
            return self._process_metric_response(response, resource_uri)

        except Exception as e:
            print(f"Error fetching CPU metrics: {e}")
            return MetricResponse(value=[])

    async def get_vm_memory_metrics(self, duration_minutes: int = 60) -> MetricResponse:
        """
        Fetches Available Memory Bytes metrics for the configured VM from Azure Monitor.
        """
        try:
            resource_uri = self._get_vm_resource_uri()
            print(f"Fetching Memory metrics for resource ID: {resource_uri}")

            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=duration_minutes)

            response = self.metrics_client.query_resource(
                resource_uri=resource_uri,
                metric_names=["Available Memory Bytes"], # Specific metric name for memory
                timespan=(start_time, end_time),
                granularity=timedelta(minutes=1),
                aggregations=[MetricAggregationType.AVERAGE] # Average is common for memory
            )
            return self._process_metric_response(response, resource_uri)

        except Exception as e:
            print(f"Error fetching Memory metrics: {e}")
            return MetricResponse(value=[])

    async def get_vm_network_metrics(self, duration_minutes: int = 60) -> MetricResponse:
        """
        Fetches Network In Total and Network Out Total metrics for the configured VM from Azure Monitor.
        """
        try:
            resource_uri = self._get_vm_resource_uri()
            print(f"Fetching Network metrics for resource ID: {resource_uri}")

            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=duration_minutes)

            response = self.metrics_client.query_resource(
                resource_uri=resource_uri,
                metric_names=["Network In Total", "Network Out Total"], # Two network metrics
                timespan=(start_time, end_time),
                granularity=timedelta(minutes=1),
                # For total bytes, SUM aggregation is often more appropriate than average.
                # However, for charts, average over small intervals can also work.
                # Let's use AVERAGE for consistency with CPU/Memory for now, but SUM is an alternative.
                aggregations=[MetricAggregationType.AVERAGE]
            )
            return self._process_metric_response(response, resource_uri)

        except Exception as e:
            print(f"Error fetching Network metrics: {e}")
            return MetricResponse(value=[])

# Example usage (for testing purposes, not part of the FastAPI app flow)
# import asyncio
# async def test_all_metrics():
#     service = AzureMonitorService()
#     cpu_metrics = await service.get_vm_cpu_metrics(duration_minutes=5)
#     print(f"CPU Metrics: {cpu_metrics.json(indent=2)}")
#     memory_metrics = await service.get_vm_memory_metrics(duration_minutes=5)
#     print(f"Memory Metrics: {memory_metrics.json(indent=2)}")
#     network_metrics = await service.get_vm_network_metrics(duration_minutes=5)
#     print(f"Network Metrics: {network_metrics.json(indent=2)}")

# if __name__ == "__main__":
#     asyncio.run(test_all_metrics())
