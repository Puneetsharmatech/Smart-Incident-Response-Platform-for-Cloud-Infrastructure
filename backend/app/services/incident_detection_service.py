# backend/app/services/incident_detection_service.py

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone # Import timezone here!

# Import our data models for metrics
from app.models.metric_data import MetricResponse, MetricValue, Metric

# Define a simple Incident model for now. We'll enhance this when we add a database.
class Incident:
    """Represents a detected incident."""
    def __init__(self,
                 incident_type: str,
                 resource_id: str,
                 timestamp: datetime,
                 details: str,
                 severity: str = "Medium"):
        self.incident_type = incident_type
        self.resource_id = resource_id
        self.timestamp = timestamp
        self.details = details
        self.severity = severity

    def to_dict(self):
        """Converts the Incident object to a dictionary for easy serialization."""
        return {
            "incident_type": self.incident_type,
            "resource_id": self.resource_id,
            "timestamp": self.timestamp.isoformat(), # ISO format for datetime
            "details": self.details,
            "severity": self.severity
        }

class IncidentDetectionService:
    """
    Service class to detect incidents based on incoming metric data.
    """
    def __init__(self):
        self.cpu_threshold_percent = 80.0
        self.cpu_duration_minutes = 5
        self.memory_threshold_gb = 2.0
        self.memory_duration_minutes = 5
        self.network_threshold_kbps = 100.0
        self.network_duration_minutes = 5

    def _get_recent_average(self, data_points: List[MetricValue], duration_minutes: int) -> Optional[float]:
        """
        Calculates the average of a metric over the most recent 'duration_minutes'.
        Assumes data_points are sorted by timestamp.
        """
        if not data_points:
            return None

        now = datetime.now(timezone.utc) # Use datetime.now() with timezone.utc

        recent_data = [
            dp.average for dp in data_points
            if dp.timeStamp is not None and dp.average is not None and (now - dp.timeStamp) <= timedelta(minutes=duration_minutes)
        ]

        if not recent_data:
            return None
        return sum(recent_data) / len(recent_data)

    def detect_cpu_incident(self, cpu_metrics: MetricResponse) -> Optional[Incident]:
        """
        Detects a high CPU incident.
        """
        if not cpu_metrics.value or not cpu_metrics.value[0].timeseries:
            return None

        cpu_data = cpu_metrics.value[0].timeseries[0].data
        resource_id = cpu_metrics.value[0].resourceId

        recent_avg_cpu = self._get_recent_average(cpu_data, self.cpu_duration_minutes)

        if recent_avg_cpu is not None and recent_avg_cpu >= self.cpu_threshold_percent:
            return Incident(
                incident_type="High CPU Utilization",
                resource_id=resource_id,
                timestamp=datetime.utcnow(),
                details=f"Average CPU usage ({recent_avg_cpu:.2f}%) exceeded threshold ({self.cpu_threshold_percent}%) for the last {self.cpu_duration_minutes} minutes.",
                severity="High"
            )
        return None

    def detect_memory_incident(self, memory_metrics: MetricResponse) -> Optional[Incident]:
        """
        Detects a low available memory incident.
        """
        if not memory_metrics.value or not memory_metrics.value[0].timeseries:
            return None

        memory_data = memory_metrics.value[0].timeseries[0].data
        resource_id = memory_metrics.value[0].resourceId

        recent_avg_memory_bytes = self._get_recent_average(memory_data, self.memory_duration_minutes)

        if recent_avg_memory_bytes is not None:
            recent_avg_memory_gb = recent_avg_memory_bytes / (1024 * 1024 * 1024)
            if recent_avg_memory_gb <= self.memory_threshold_gb:
                return Incident(
                    incident_type="Low Available Memory",
                    resource_id=resource_id,
                    timestamp=datetime.utcnow(),
                    details=f"Average available memory ({recent_avg_memory_gb:.2f} GB) fell below threshold ({self.memory_threshold_gb} GB) for the last {self.memory_duration_minutes} minutes.",
                    severity="High"
                )
        return None

    def detect_network_incident(self, network_metrics: MetricResponse) -> Optional[Incident]:
        """
        Detects high network traffic (in or out) incident.
        """
        if not network_metrics.value or len(network_metrics.value) < 2 or \
           not network_metrics.value[0].timeseries or not network_metrics.value[1].timeseries:
            return None

        # FIX: Access 'value' key from the 'name' dictionary
        network_in_metric = next((m for m in network_metrics.value if m.name['value'] == "Network In Total"), None)
        network_out_metric = next((m for m in network_metrics.value if m.name['value'] == "Network Out Total"), None)

        if not network_in_metric or not network_out_metric:
            return None

        network_in_data = network_in_metric.timeseries[0].data
        network_out_data = network_out_metric.timeseries[0].data
        resource_id = network_in_metric.resourceId

        recent_avg_in_bytes = self._get_recent_average(network_in_data, self.network_duration_minutes)
        recent_avg_out_bytes = self._get_recent_average(network_out_data, self.network_duration_minutes)

        if recent_avg_in_bytes is not None and recent_avg_out_bytes is not None:
            recent_avg_in_kbps = recent_avg_in_bytes / 1024
            recent_avg_out_kbps = recent_avg_out_bytes / 1024
            total_traffic_kbps = recent_avg_in_kbps + recent_avg_out_kbps

            if total_traffic_kbps >= self.network_threshold_kbps:
                return Incident(
                    incident_type="High Network Traffic",
                    resource_id=resource_id,
                    timestamp=datetime.utcnow(),
                    details=f"Average total network traffic ({total_traffic_kbps:.2f} KBps) exceeded threshold ({self.network_threshold_kbps} KBps) for the last {self.network_duration_minutes} minutes. (In: {recent_avg_in_kbps:.2f} KBps, Out: {recent_avg_out_kbps:.2f} KBps)",
                    severity="Medium"
                )
        return None

    async def run_detection(self,
                            cpu_metrics: MetricResponse,
                            memory_metrics: MetricResponse,
                            network_metrics: MetricResponse) -> List[Incident]:
        """
        Runs all detection rules and returns a list of detected incidents.
        """
        detected_incidents: List[Incident] = []

        cpu_incident = self.detect_cpu_incident(cpu_metrics)
        if cpu_incident:
            detected_incidents.append(cpu_incident)

        memory_incident = self.detect_memory_incident(memory_metrics)
        if memory_incident:
            detected_incidents.append(memory_incident)

        network_incident = self.detect_network_incident(network_metrics)
        if network_incident:
            detected_incidents.append(network_incident)

        return detected_incidents
