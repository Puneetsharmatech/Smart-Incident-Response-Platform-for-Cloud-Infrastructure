# backend/app/models/metric_data.py

from pydantic import BaseModel # BaseModel is the base class for Pydantic models
from typing import List, Dict, Any # Used for type hints: List for lists, Dict for dictionaries, Any for any type
from datetime import datetime # Used for handling date and time objects

# This model represents a single data point within a metric's time series.
# Azure Monitor metrics often include various aggregation types (average, count, max, min, total).
class MetricValue(BaseModel):
    # 'timeStamp' is the datetime when this metric value was recorded.
    timeStamp: datetime
    # 'average', 'count', 'maximum', 'minimum', 'total' are optional float values.
    # 'None' as a default means the field is optional and can be missing or null.
    average: float = None
    count: float = None
    maximum: float = None
    minimum: float = None
    total: float = None

# This model represents a time series element for a metric.
# A single metric (e.g., "Percentage CPU") can have multiple time series,
# especially if it's broken down by dimensions (e.g., CPU per instance).
class MetricTimeSeriesElement(BaseModel):
    # 'data' is a list of MetricValue objects, representing the actual time-series data points.
    data: List[MetricValue]
    # You might add other fields here if Azure Monitor provides them and you need them,
    # such as 'metadata' or 'dimensions' if the metric is multi-dimensional.

# This model represents a single metric returned from Azure Monitor (e.g., "Percentage CPU").
class Metric(BaseModel):
    # 'id' is the unique identifier for the metric instance, including resource ID.
    id: str
    # 'name' is a dictionary containing the metric's name and its localized value.
    name: Dict[str, str]
    # 'type' indicates the type of the metric resource (e.g., "Microsoft.Insights/metrics").
    type: str
    # 'unit' is the unit of measurement for the metric (e.g., "Percent", "Bytes").
    unit: str
    # 'timeseries' is a list of MetricTimeSeriesElement objects, holding the actual data.
    timeseries: List[MetricTimeSeriesElement]
    # 'resourceId' is an optional field to explicitly store the Azure Resource ID
    # for which this metric was fetched. This can be useful for clarity.
    resourceId: str = None

# This is the top-level response model for fetching metrics.
# Azure Monitor's API often wraps the actual metric data in a 'value' field.
class MetricResponse(BaseModel):
    # 'value' is a list of Metric objects, representing all the metrics returned by the query.
    value: List[Metric]
