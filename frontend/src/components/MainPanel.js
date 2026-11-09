// src/components/MainPanel.js
import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import * as atlas from "azure-maps-control";
import Alerts from "./Alerts";
import "azure-maps-control/dist/atlas.min.css";

function MainPanel() {
  const [feedUrl, setFeedUrl] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [cameraLocations, setCameraLocations] = useState([]);

  // Refs
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const markersRef = useRef([]);

  // Start model
  const triggerModel = async () => {
    try {
      const response = await axios.post("http://localhost:9000/start-model");
      setFeedUrl("http://localhost:9000/video_feed");
      setIsRunning(true);
      alert(response.data.message);
    } catch (error) {
      console.error("Error starting model:", error);
      alert("Error starting surveillance.");
    }
  };

  // Stop model
  const stopModel = async () => {
    try {
      const response = await axios.post("http://localhost:9000/stop-model");
      setFeedUrl("");
      setIsRunning(false);
      alert(response.data.message);
    } catch (error) {
      console.error("Error stopping model:", error);
      alert("Error stopping surveillance.");
    }
  };

  // Fetch camera locations from backend
  useEffect(() => {
    const fetchCameraLocations = async () => {
      try {
        const response = await fetch("http://localhost:5000/camera-locations");
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

  // Initialize Azure Map
  useEffect(() => {
    const subscriptionKey = process.env.REACT_APP_AZURE_MAPS_KEY;
    if (!subscriptionKey) {
      console.error("Azure Maps key missing. Add REACT_APP_AZURE_MAPS_KEY to your .env file.");
      return;
    }
    if (!mapInstance.current && mapRef.current) {
      try {
        const map = new atlas.Map(mapRef.current, {
          center: [80.2707, 13.0827], // Chennai
          zoom: 12,
          authOptions: {
            authType: "subscriptionKey",
            subscriptionKey: subscriptionKey,
          },
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

  // Add markers when cameraLocations update
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
    // The main container is a grid with two columns
    <div className="grid grid-cols-2 gap-6 p-4 h-screen box-border">

      {/* This div is the left column, which is a nested grid */}
      <div className="grid grid-rows-[1fr_1fr] gap-6">

        {/* Live Feed Section */}
        <section className="bg-white p-6 rounded-2xl shadow-md flex flex-col min-h-0 overflow-hidden">
          <h2 className="text-xl font-semibold mb-4">Live CCTV Feed</h2>
          {feedUrl ? (
            <div className="flex-1 min-h-0 flex justify-center">
              <img
                src={feedUrl}
                alt="Live CCTV Feed"
                className="rounded-xl shadow-lg w-full h-full object-contain border border-gray-300"
                onError={(e) => {
                  console.error("Error loading video feed");
                  e.target.style.display = "none";
                }}
              />
            </div>
          ) : (
            <p className="text-gray-500 text-center flex-1 flex items-center justify-center">
              Click <b>Start Surveillance</b> to view the live feed.
            </p>
          )}
          <div className="flex justify-center gap-4 mt-6">
            {!isRunning ? (
              <button
                onClick={triggerModel}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-md transition"
              >
                Start Surveillance
              </button>
            ) : (
              <button
                onClick={stopModel}
                className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg shadow-md transition"
              >
                Stop Surveillance
              </button>
            )}
          </div>
        </section>

        {/* Map Section */}
        <section className="bg-white p-6 rounded-2xl shadow-md flex flex-col min-h-0 overflow-hidden">
          <h2 className="text-xl font-semibold mb-4">Camera Locations Map</h2>
          <div className="text-sm text-gray-600 mb-4">
            {cameraLocations.length > 0
              ? `Showing ${cameraLocations.length} camera(s) on the map`
              : "Loading camera locations..."}
          </div>
          <div
            ref={mapRef}
            className="flex-1 min-h-0 rounded-xl border border-gray-300 overflow-hidden"
          />
        </section>
      </div>

      {/* The Alerts component occupies the entire right column */}
      <section className="bg-white p-6 rounded-2xl shadow-md flex flex-col min-h-0 overflow-hidden">
        <Alerts />
      </section>
    </div>
  );
}

export default MainPanel;