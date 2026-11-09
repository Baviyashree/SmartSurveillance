import { useEffect, useState } from "react";

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);

  // Fetch alerts from Flask API
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch("http://localhost:5000/api/alerts"); // Flask route
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        
        // Ensure data is an array
        if (Array.isArray(data)) {
          setAlerts(data);
        } else {
          console.error("Expected array but got:", data);
          setAlerts([]);
        }
      } catch (err) {
        console.error("Error fetching alerts:", err);
        setAlerts([]); // Ensure alerts remains an array on error
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000); // refresh every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white p-6 rounded-2xl shadow-md mt-6">
      <h2 className="text-xl font-semibold mb-2">📢 Alerts from Database</h2>
    
      {alerts.length === 0 ? (
        <p className="text-gray-500">No alerts found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-gray-100 text-left text-gray-700">
                <th className="p-3 border-b">ID</th>
                <th className="p-3 border-b">Camera ID</th>
                <th className="p-3 border-b">Keyword</th>
                <th className="p-3 border-b">Location (Lat, Lng)</th>
                <th className="p-3 border-b">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert) => (
                <tr key={alert.id} className="hover:bg-gray-50">
                  <td className="p-3 border-b">{alert.id}</td>
                  <td className="p-3 border-b">{alert.camera_id}</td>
                  <td
                    className={`p-3 border-b font-semibold ${
                      alert.keyword === "Yes"
                        ? "text-green-600"
                        : alert.keyword === "No"
                        ? "text-red-600"
                        : "text-gray-700"
                    }`}
                  >
                    {alert.keyword}
                  </td>
                  <td className="p-3 border-b">
                    {alert.lat && alert.lng 
                      ? `${parseFloat(alert.lat).toFixed(4)}, ${parseFloat(alert.lng).toFixed(4)}`
                      : 'N/A'
                    }
                  </td>
                  <td className="p-3 border-b">
                    {new Date(alert.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}