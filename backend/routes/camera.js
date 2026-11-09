// backend/routes/cameras.js
const express = require("express");
const router = express.Router();
const db = require("../db/db");

router.get("/camera-locations", async (req, res) => {
  try {
    const [rows] = await db.execute("SELECT camera_id, lat, lng FROM cameras");
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
