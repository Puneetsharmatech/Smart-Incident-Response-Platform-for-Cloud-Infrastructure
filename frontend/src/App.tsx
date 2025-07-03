// src/App.tsx

import React from 'react';
import MetricDisplay from './components/MetricDisplay'; // Import the reusable MetricDisplay component
import IncidentList from './components/IncidentList'; // Import the new IncidentList component

function App() {
  return (
    // Main container for the entire application, full height, light background, padding
    <div className="min-h-screen bg-gray-100 p-4">
      {/* Header section */}
      <header className="text-center mb-8">
        <h1 className="text-4xl font-extrabold text-blue-800 mb-2">
          Smart Incident Response Platform
        </h1>
        <p className="text-lg text-gray-700">
          Real-time monitoring and anomaly detection for cloud infrastructure.
        </p>
      </header>

      {/* Main content area for charts. */}
      <main className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {/* CPU Metrics Chart */}
        <MetricDisplay
          metricType="cpu"
          title="CPU Utilization"
          yAxisLabel="CPU (%)"
          lineColor="#8884d8" // Purple
        />

        {/* Memory Metrics Chart */}
        <MetricDisplay
          metricType="memory"
          title="Available Memory"
          yAxisLabel="Memory (GB)"
          lineColor="#82ca9d" // Green
        />

        {/* Network Metrics Chart */}
        <MetricDisplay
          metricType="network"
          title="Network Traffic"
          yAxisLabel="Traffic (KBps)"
          lineColor="#ffc658" // Yellow (Note: Network will have two lines, this is for the first)
        />
      </main>

      {/* Incident List Section */}
      <section className="mt-8">
        <IncidentList />
      </section>
    </div>
  );
}

export default App;
