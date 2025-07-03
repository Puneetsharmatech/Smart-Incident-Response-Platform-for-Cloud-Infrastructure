// frontend/src/components/MetricDisplay.tsx

import React, { useState, useEffect, useMemo } from 'react'; // Import React, hooks, and useMemo for optimization
// Import Recharts components for creating a line chart
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// --- Data Model Interfaces ---
// Define the shape of the data we expect from the backend.
// This should match the Pydantic models we defined in the backend.
interface MetricValue {
  timeStamp: string; // Dates often come as strings from APIs, we can parse them later
  average: number | null;
  count?: number | null; // Optional fields, as they might be null from API
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

// Define the MetricDisplay functional component.
const MetricDisplay: React.FC = () => {
  // Use useState to manage the data fetched from the API.
  const [metrics, setMetrics] = useState<MetricResponse | null>(null);
  // 'loading' state to show a loading indicator.
  const [loading, setLoading] = useState<boolean>(true);
  // 'error' state to store any error messages.
  const [error, setError] = useState<string | null>(null);

  // useEffect hook to perform data fetching when the component mounts.
  // The empty dependency array '[]' ensures this effect runs only once after the initial render.
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const backendUrl = process.env.REACT_APP_BACKEND_API_URL;
        if (!backendUrl) {
          throw new Error("Backend API URL is not defined in environment variables.");
        }

        const url = `${backendUrl}/api/v1/metrics/cpu/60`; // Fetch 60 minutes of data for a better chart
        console.log("Fetching from:", url); // Log the URL for debugging

        const response = await fetch(url);

        if (!response.ok) {
          const errorData = await response.json(); // Try to parse error message from response body
          throw new Error(`HTTP error! status: ${response.status}, detail: ${errorData.detail || response.statusText}`);
        }

        const data: MetricResponse = await response.json();
        console.log("Fetched data:", data); // Log the fetched data for debugging

        setMetrics(data);
      } catch (err: any) {
        // Catch any errors during the fetch process and update the 'error' state.
        console.error("Error fetching metrics:", err);
        setError(err.message);
      } finally {
        // In either case (success or error), set 'loading' to false.
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []); // Empty dependency array means this effect runs only once on mount.

  // --- Data Transformation for Recharts ---
  // useMemo memoizes the result of this function. It will only re-run if 'metrics' changes.
  // This prevents unnecessary re-calculations on every render.
  const chartData = useMemo(() => {
    if (!metrics || metrics.value.length === 0 || !metrics.value[0].timeseries.length) {
      return [];
    }
    // Assuming we are only interested in the first metric (CPU) and its first time series.
    const cpuMetricData = metrics.value[0].timeseries[0].data;

    return cpuMetricData.map(dataPoint => ({
      // Format timestamp for X-axis (e.g., "10:30 AM")
      name: new Date(dataPoint.timeStamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      // Assign the average CPU value to a key 'cpu'
      cpu: dataPoint.average ? parseFloat(dataPoint.average.toFixed(2)) : 0, // Ensure it's a number, fix to 2 decimal places
    }));
  }, [metrics]); // Recalculate chartData whenever 'metrics' state changes.
  // --- End Data Transformation ---


  // Render the component's UI based on its state.
  if (loading) {
    return (
      <div className="text-center p-4">
        <p className="text-gray-600">Loading CPU metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-4 text-red-600">
        <p>Error: {error}</p>
        <p>Please ensure your backend is running and accessible.</p>
      </div>
    );
  }

  return (
    <div className="mt-8 p-4 bg-gray-50 rounded-lg shadow-inner w-full">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4 text-center">CPU Utilization (Last 60 Minutes)</h2>

      {/* Check if we have data to display in the chart */}
      {chartData.length > 0 ? (
        // ResponsiveContainer makes the chart responsive to its parent's size.
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={chartData} // Pass the transformed data to the chart
            margin={{
              top: 5, right: 30, left: 20, bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" /> {/* Grid lines */}
            <XAxis dataKey="name" /> {/* X-axis for time */}
            <YAxis label={{ value: 'CPU (%)', angle: -90, position: 'insideLeft' }} /> {/* Y-axis for CPU percentage */}
            <Tooltip /> {/* Displays data on hover */}
            <Legend /> {/* Legend for the line (e.g., "CPU") */}
            {/* The Line component defines the actual line on the chart.
                dataKey="cpu" links it to the 'cpu' key in our chartData.
                stroke sets the line color. */}
            <Line type="monotone" dataKey="cpu" stroke="#8884d8" activeDot={{ r: 8 }} />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <p className="text-center text-gray-600">No CPU metrics data available to display chart.</p>
      )}

      {/* Optional: Keep raw data display for debugging if needed, or remove it */}
      {/*
      <div className="mt-4 text-left">
        <h3 className="text-xl font-medium text-blue-700 mb-2">Raw Data Points:</h3>
        {metrics && metrics.value.length > 0 && metrics.value[0].timeseries.length > 0 && (
          <ul className="list-disc list-inside text-gray-700 max-h-48 overflow-y-auto">
            {metrics.value[0].timeseries[0].data.map((dataPoint, index) => (
              <li key={index}>
                {new Date(dataPoint.timeStamp).toLocaleString()}: Average {dataPoint.average?.toFixed(2)}%
              </li>
            ))}
          </ul>
        )}
      </div>
      */}
    </div>
  );
};

export default MetricDisplay;
