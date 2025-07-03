// frontend/src/components/IncidentList.tsx

import React, { useState, useEffect } from 'react';

// Define the interface for an Incident, matching the backend's Incident.to_dict() structure.
interface Incident {
  incident_type: string;
  resource_id: string;
  timestamp: string; // Will be a string, parse to Date for display
  details: string;
  severity: 'Low' | 'Medium' | 'High' | 'Critical'; // Define possible severities
}

const IncidentList: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const backendUrl = process.env.REACT_APP_BACKEND_API_URL;
        if (!backendUrl) {
          throw new Error("Backend API URL is not defined in environment variables.");
        }

        const url = `${backendUrl}/api/v1/incidents/detect`; // Endpoint to detect incidents
        console.log("Fetching incidents from:", url);

        const response = await fetch(url);

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(`HTTP error! status: ${response.status}, detail: ${errorData.detail || response.statusText}`);
        }

        const data: Incident[] = await response.json();
        console.log("Fetched incidents:", data);

        setIncidents(data);
      } catch (err: any) {
        console.error("Error fetching incidents:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    // Fetch incidents initially and then every 30 seconds (for near real-time updates)
    fetchIncidents(); // Initial fetch
    const intervalId = setInterval(fetchIncidents, 30000); // Fetch every 30 seconds

    // Cleanup function: Clear the interval when the component unmounts
    return () => clearInterval(intervalId);
  }, []); // Empty dependency array means this effect runs only once on mount and cleans up on unmount.

  // Helper function to get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-blue-100 text-blue-800';
      case 'critical':
        return 'bg-red-700 text-white'; // More prominent for critical
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="text-center p-4">
        <p className="text-gray-600">Checking for incidents...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-4 text-red-600">
        <p>Error loading incidents: {error}</p>
      </div>
    );
  }

  return (
    <div className="mt-8 p-6 bg-white rounded-lg shadow-lg max-w-6xl mx-auto">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4 text-center">Detected Incidents</h2>
      {incidents.length > 0 ? (
        <div className="space-y-4">
          {incidents.map((incident, index) => (
            <div key={index} className={`p-4 rounded-lg border ${getSeverityColor(incident.severity)}`}>
              <div className="flex items-center justify-between mb-2">
                <span className={`font-bold text-lg ${incident.severity.toLowerCase() === 'high' || incident.severity.toLowerCase() === 'critical' ? 'text-red-800' : ''}`}>
                  {incident.incident_type}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getSeverityColor(incident.severity)}`}>
                  {incident.severity}
                </span>
              </div>
              <p className="text-sm mb-1">
                <span className="font-medium">Resource:</span> <code className="bg-gray-200 rounded px-1 py-0.5 text-xs">{incident.resource_id.split('/').pop()}</code>
              </p>
              <p className="text-sm mb-1">
                <span className="font-medium">Time:</span> {new Date(incident.timestamp).toLocaleString()}
              </p>
              <p className="text-sm">
                <span className="font-medium">Details:</span> {incident.details}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-center text-gray-600">No active incidents detected. All clear!</p>
      )}
    </div>
  );
};

export default IncidentList;
