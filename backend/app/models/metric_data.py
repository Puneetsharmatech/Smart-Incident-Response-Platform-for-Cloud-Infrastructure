# backend/app/models/metric_data.py

from pydantic import BaseModel
from typing import List, Dict, Any, Optional # Import Optional for truly optional fields
from datetime import datetime

# This model represents a single data point within a metric's time series.
# Azure Monitor metrics often include various aggregation types (average, count, max, min, total).
class MetricValue(BaseModel):
    timeStamp: datetime
    average: Optional[float] = None # Use Optional[float] to explicitly allow None
    count: Optional[float] = None   # Use Optional[float] to explicitly allow None
    maximum: Optional[float] = None # Use Optional[float] to explicitly allow None
    minimum: Optional[float] = None # Use Optional[float] to explicitly allow None
    total: Optional[float] = None   # Use Optional[float] to explicitly allow None

# This model represents a time series element for a metric.
class MetricTimeSeriesElement(BaseModel):
    data: List[MetricValue]

# This model represents a single metric returned from Azure Monitor.
class Metric(BaseModel):
    id: str
    name: Dict[str, str]
    type: str
    unit: str
    timeseries: List[MetricTimeSeriesElement]
    resourceId: str = None

# This is the top-level response model for fetching metrics.
class MetricResponse(BaseModel):
    value: List[Metric]
