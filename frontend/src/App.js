// src/App.js
import React from "react";
import Navbar from "./components/Navbar";
import MainPanel from "./components/MainPanel";
import Dashboard from "./components/Dashboardog";

function App() {
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Top Navbar */}
      <Navbar />

      {/* Sidebar + Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}

        {/* Main Panel */}
        <main className="flex-1 overflow-hidden">
          {/* Removed max-w-5xl wrapper to allow full width */}
          <Dashboard />
        </main>
      </div>
    </div>
  );
}

export default App;
