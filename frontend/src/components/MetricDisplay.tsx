// frontend/src/components/MetricDisplay.tsx

import React, { useState, useEffect, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// --- Data Model Interfaces (unchanged) ---
interface MetricValue {
  timeStamp: string;
  average: number | null;
  count?: number | null;
  maximum?: number | null;
  minimum?: number | null;
  total?: number | null;
}

interface MetricTimeSeriesElement {
  data: MetricValue[];
}

interface Metric {
  id: string;
  name: { value: string; localizedValue: string };
  type: string;
  unit: string;
  timeseries: MetricTimeSeriesElement[];
  resourceId: string;
}

interface MetricResponse {
  value: Metric[];
}
// --- End Data Model Interfaces ---

// Define props interface for MetricDisplay component
interface MetricDisplayProps {
  metricType: 'cpu' | 'memory' | 'network'; // Specifies which type of metric to display
  title: string; // Title for the chart
  yAxisLabel: string; // Label for the Y-axis
  lineColor: string; // Color of the chart line
}

// Define the MetricDisplay functional component, now accepting props.
const MetricDisplay: React.FC<MetricDisplayProps> = ({ metricType, title, yAxisLabel, lineColor }) => {
  const [metrics, setMetrics] = useState<MetricResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const backendUrl = process.env.REACT_APP_BACKEND_API_URL;
        if (!backendUrl) {
          throw new Error("Backend API URL is not defined in environment variables.");
        }

        // Dynamically construct the URL based on metricType prop
        const url = `${backendUrl}/api/v1/metrics/${metricType}/60`; // Fetch 60 minutes of data
        console.log(`Fetching ${metricType} from:`, url);

        const response = await fetch(url);

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(`HTTP error! status: ${response.status}, detail: ${errorData.detail || response.statusText}`);
        }

        const data: MetricResponse = await response.json();
        console.log(`Fetched ${metricType} data:`, data);

        setMetrics(data);
      } catch (err: any) {
        console.error(`Error fetching ${metricType} metrics:`, err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    // Re-run effect if metricType changes (though in App.tsx we'll use fixed types)
  }, [metricType]);

  // --- Data Transformation for Recharts ---
  const chartData = useMemo(() => {
    if (!metrics || metrics.value.length === 0 || !metrics.value[0].timeseries.length) {
      return [];
    }

    // For network metrics, we might have two lines (In and Out).
    // For CPU and Memory, we expect one primary metric.
    const primaryMetricData = metrics.value[0].timeseries[0].data;

    if (metricType === 'network' && metrics.value.length > 1) {
      // If network, assume first is Network In, second is Network Out
      const networkInData = metrics.value.find(m => m.name.value === "Network In Total")?.timeseries[0]?.data || [];
      const networkOutData = metrics.value.find(m => m.name.value === "Network Out Total")?.timeseries[0]?.data || [];

      // Merge data points by timestamp
      const mergedData: { [key: string]: { name: string; 'Network In (KBps)': number; 'Network Out (KBps)': number } } = {};

      networkInData.forEach(dp => {
        const time = new Date(dp.timeStamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        mergedData[time] = {
          ...mergedData[time],
          name: time,
          'Network In (KBps)': dp.average ? parseFloat((dp.average / 1024).toFixed(2)) : 0, // Convert bytes to KB
        };
      });

      networkOutData.forEach(dp => {
        const time = new Date(dp.timeStamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        mergedData[time] = {
          ...mergedData[time],
          name: time,
          'Network Out (KBps)': dp.average ? parseFloat((dp.average / 1024).toFixed(2)) : 0, // Convert bytes to KB
        };
      });

      return Object.values(mergedData).sort((a, b) => a.name.localeCompare(b.name)); // Sort by time
    } else {
      // For CPU and Memory, process a single metric
      return primaryMetricData.map(dataPoint => {
        let value = 0;
        let unit = '';
        if (metricType === 'cpu') {
          value = dataPoint.average ? parseFloat(dataPoint.average.toFixed(2)) : 0;
          unit = '%';
        } else if (metricType === 'memory') {
          // Convert bytes to GB for better readability
          value = dataPoint.average ? parseFloat((dataPoint.average / (1024 * 1024 * 1024)).toFixed(2)) : 0;
          unit = 'GB';
        }

        return {
          name: new Date(dataPoint.timeStamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          value: value, // Generic 'value' key for single metrics
          unit: unit // Store unit for Y-axis label
        };
      });
    }
  }, [metrics, metricType]);
  // --- End Data Transformation ---


  if (loading) {
    return (
      <div className="text-center p-4 min-h-[350px] flex items-center justify-center">
        <p className="text-gray-600">Loading {title} metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-4 text-red-600 min-h-[350px] flex items-center justify-center">
        <p>Error loading {title}: {error}</p>
        <p>Please ensure your backend is running and accessible.</p>
      </div>
    );
  }

  return (
    <div className="mt-8 p-4 bg-white rounded-lg shadow-lg w-full">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4 text-center">{title}</h2>

      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={chartData}
            margin={{
              top: 5, right: 30, left: 20, bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            {metricType === 'network' ? (
              <>
                <Line type="monotone" dataKey="Network In (KBps)" stroke="#82ca9d" activeDot={{ r: 8 }} />
                <Line type="monotone" dataKey="Network Out (KBps)" stroke="#8884d8" activeDot={{ r: 8 }} />
              </>
            ) : (
              <Line type="monotone" dataKey="value" stroke={lineColor} activeDot={{ r: 8 }} />
            )}
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <p className="text-center text-gray-600">No {title} data available to display chart.</p>
      )}
    </div>
  );
};

export default MetricDisplay;
