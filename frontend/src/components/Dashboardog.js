import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./Dashboard.css";
import * as atlas from "azure-maps-control";
import "azure-maps-control/dist/atlas.min.css";

const Dashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [feedUrl, setFeedUrl] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [cameraLocations, setCameraLocations] = useState([]);

  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const markersRef = useRef([]);

  // 🚨 Fetch Alerts (limited to 9)
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch("http://localhost:5000/api/alerts");
        // const res = await fetch("https://g2bmbrr7-5000.inc1.devtunnels.ms//api/alerts");
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();

        if (Array.isArray(data)) {
          // sort newest first & take only latest 9
          const sorted = data.sort(
            (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
          );
          setAlerts(sorted.slice(0, 10));
        } else {
          console.error("Expected array but got:", data);
          setAlerts([]);
        }
      } catch (err) {
        console.error("Error fetching alerts:", err);
        setAlerts([]);
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000);
    return () => clearInterval(interval);
  }, []);

  // 🎥 Start the surveillance model
  const triggerModel = async () => {
    try {
      // const response = await axios.post("https://g2bmbrr7-9000.inc1.devtunnels.ms/start-model");
    const response = await axios.post("http://localhost:9000/start-model");
      setFeedUrl("http://localhost:9000/video_feed");
    // setFeedUrl("https://g2bmbrr7-9000.inc1.devtunnels.ms/video_feed");
      setIsRunning(true);
      alert(response.data.message);
    } catch (error) {
      console.error("Error starting model:", error);
      alert("Error starting surveillance.");
    }
  };

  // 🛑 Stop the surveillance model
  const stopModel = async () => {
    try {
      const response = await axios.post("http://localhost:9000/stop-model");
      // const response = await axios.post("https://g2bmbrr7-9000.inc1.devtunnels.ms/stop-model");
      setFeedUrl("");
      setIsRunning(false);
      alert(response.data.message);
    } catch (error) {
      console.error("Error stopping model:", error);
      alert("Error stopping surveillance.");
    }
  };

  // 📡 Fetch camera locations
  useEffect(() => {
    const fetchCameraLocations = async () => {
      try {
        const response = await fetch("http://localhost:5000/camera-locations");
        //  const response = await fetch("https://g2bmbrr7-5000.inc1.devtunnels.ms/camera-locations");
        if (response.ok) {
          const data = await response.json();
          setCameraLocations(data);
        } else {
          console.error("Failed to fetch camera locations:", response.statusText);
        }
      } catch (err) {
        console.error("Error fetching camera locations:", err);
      }
    };

    fetchCameraLocations();
  }, []);

  // 🗺️ Initialize Azure Map
  useEffect(() => {
    const subscriptionKey = process.env.REACT_APP_AZURE_MAPS_KEY;
    if (!subscriptionKey) {
      console.error("Azure Maps key missing. Add REACT_APP_AZURE_MAPS_KEY to your .env file.");
      return;
    }

    if (!mapInstance.current && mapRef.current) {
      try {
        const map = new atlas.Map(mapRef.current, {
          center: [80.2707, 13.0827],
          zoom: 12,
          authOptions: { authType: "subscriptionKey", subscriptionKey },
          style: "road",
        });

        map.controls.add(new atlas.control.ZoomControl(), { position: "top-right" });
        map.controls.add(new atlas.control.StyleControl(), { position: "top-left" });

        map.events.add("ready", () => {
          console.log("✅ Azure Map initialized");
        });

        mapInstance.current = map;
      } catch (error) {
        console.error("Error initializing Azure Map:", error);
      }
    }

    return () => {
      if (mapInstance.current) {
        mapInstance.current.dispose();
        mapInstance.current = null;
      }
    };
  }, []);

  // 📍 Add markers
  useEffect(() => {
    if (mapInstance.current && cameraLocations.length > 0) {
      markersRef.current.forEach(marker => {
        mapInstance.current.markers.remove(marker);
      });
      markersRef.current = [];

      cameraLocations.forEach((cam, index) => {
        try {
          const popup = new atlas.Popup({
            content: `<div style="padding: 10px;">
              <h4>${cam.name || `Camera ${cam.camera_id}`}</h4>
              <p><b>ID:</b> ${cam.camera_id}</p>
              <p><b>Location:</b> ${cam.lat}, ${cam.lng}</p>
              <p><b>Status:</b> ${cam.status || "inactive"}</p>
            </div>`,
            pixelOffset: [0, -18],
          });

          const marker = new atlas.HtmlMarker({
            color: cam.status === "active" ? "green" : "red",
            text: (cam.camera_id || index + 1).toString(),
            position: [parseFloat(cam.lng), parseFloat(cam.lat)],
          });

          mapInstance.current.markers.add(marker);
          mapInstance.current.events.add("click", marker, () => {
            popup.open(mapInstance.current, marker.getOptions().position);
          });

          markersRef.current.push(marker);
        } catch (error) {
          console.error(`Error adding marker for camera ${cam.camera_id}:`, error);
        }
      });

      console.log(`✅ Added ${cameraLocations.length} markers`);
    }
  }, [cameraLocations]);

  return (
    <div className="dashboard">
      <div className="left">
        <h2>Live CCTV Feed</h2>

        {isRunning && feedUrl ? (
          <img
            src={feedUrl}
            alt="Live CCTV Feed"
            style={{ width: "85%", height: "300px", objectFit: "cover", objectPosition: "center", background: "#000" }}
            onError={(e) => { console.error("Error loading video feed"); e.target.style.display = "none"; }}
          />
        ) : (
          <p>Start the surveillance to activate the camera and view the live feed.</p>
        )}

        <button className="start-btn" onClick={isRunning ? stopModel : triggerModel}>
          {isRunning ? "Stop Surveillance" : "Start Surveillance"}
        </button>

        <h2>📢 Alerts from Database</h2>
        {alerts.length === 0 ? (
          <p className="text-gray-500">No alerts found.</p>
        ) : (
          <div className="overflow-y-auto" style={{ maxHeight: "220px" }}>
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-gray-100 text-left text-gray-700 sticky top-0">
                  <th className="p-2 border-b">ID</th>
                  <th className="p-2 border-b">Camera ID</th>
                  <th className="p-2 border-b">Keyword</th>
                  <th className="p-2 border-b">Emotion</th>
                  <th className="p-2 border-b">Location</th>
                  <th className="p-2 border-b">Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-gray-50">
                    <td className="p-2 border-b">{alert.id}</td>
                    <td className="p-2 border-b">{alert.camera_id}</td>
                    <td
                      className={`p-2 border-b font-semibold ${
                        alert.keyword?.toLowerCase() === "Yes"
                          ? "text-green-600"
                          : alert.keyword?.toLowerCase() === "No"
                          ? "text-red-600"
                          : "text-gray-700"
                      }`}
                    >
                      {alert.keyword}
                    </td>
                    <td className="p-2 border-b">
  {alert.emotion ? alert.emotion : "unknown"}
</td>
                    <td className="p-2 border-b">
                      {alert.lat && alert.lng
                        ? `${parseFloat(alert.lat).toFixed(4)}, ${parseFloat(alert.lng).toFixed(4)}`
                        : "N/A"}
                    </td>
                    <td className="p-2 border-b">{new Date(alert.timestamp).toUTCString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="right">
        <h2>Camera Location Map</h2>
        <div ref={mapRef} style={{ height: "400px", width: "100%" }} />
      </div>
    </div>
  );
};

export default Dashboard;
