const db = require("../db/db");
const twilio = require("twilio");

const client = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN,
);

const CAMERA_LOCATIONS = {
  cam01: { lat: 13.0827, lng: 80.2707 },
  cam02: { lat: 13.085, lng: 80.274 },
  cam03: { lat: 13.08, lng: 80.268 },
  cam04: { lat: 13.0835, lng: 80.272 },
};
const saveAlert = async (req, res) => {
  let { camera_id, keyword, emotion, lat, lng, timestamp } = req.body;
  camera_id = camera_id || "unknown";
  // lat = lat ?? null;  // null instead of undefined
  // lng = lng ?? null;
  if (!lat || !lng) {
    const location = CAMERA_LOCATIONS[camera_id];
    if (location) {
      lat = location.lat ?? null; // null instead of undefined
      lng = location.lng ?? null;
    } else {
      lat = null;
      lng = null;
    }
  }

  timestamp = timestamp || new Date();

  try {
    // ✅ Use new variable
    let mappedKeyword = "no";
    if (keyword && keyword.trim() !== "") {
      mappedKeyword = "yes";
    }

    const [result] = await db.execute(
      "INSERT INTO alerts2 (camera_id, keyword,emotion, lat, lng, timestamp) VALUES (?, ?, ?,?, ?, ?)",
      [camera_id, mappedKeyword, emotion, lat, lng, timestamp],
    );

    console.log(
      `[DB] Alert saved: Camera=${camera_id}, Keyword=${mappedKeyword},Emotion=${emotion}, Location=(${lat}, ${lng})`,
    );

    const mapsUrl = `https://www.bing.com/maps?cp=${lat}~${lng}&lvl=17`; // you can replace with Azure Maps later
    const alertMsg = `🚨 ALERT from ${camera_id}\nTime: ${timestamp}\nUrl: ${mapsUrl}`;

    await client.messages.create({
      body: alertMsg,
      from: process.env.TWILIO_PHONE, // Twilio number
      to: process.env.RESCUE_TEAM_PHONE, // Rescue team number
    });

    console.log("✅ Rescue team notified via SMS");

    res.status(201).json({ message: "Alert saved & rescue team notified" });
  } catch (err) {
    console.error("❌ DB/Twilio error:", err);
    res.status(500).json({ error: err.message });
  }
};
console.log("🔍 Twilio ENV Check:");
console.log("From:", process.env.TWILIO_PHONE);
console.log("To:", process.env.RESCUE_TEAM_PHONE);

console.log("✅ SMS sent to rescue team!");

const getAlerts = async (req, res) => {
  try {
    const [rows] = await db.execute(
      "SELECT * FROM alerts2 ORDER BY timestamp DESC",
    );
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

module.exports = { saveAlert, getAlerts };
