    // src/App.tsx

    import React from 'react';
    import MetricDisplay from './components/MetricDisplay'; // Import the new component

    function App() {
      return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center max-w-md w-full">
            <h1 className="text-3xl font-bold text-blue-600 mb-4">
              Smart Incident Response Platform
            </h1>
            <p className="text-gray-700">
              Frontend is ready! Let's build something amazing.
            </p>

            {/* Render our new MetricDisplay component here */}
            <MetricDisplay />

          </div>
        </div>
      );
    }

    export default App;
    