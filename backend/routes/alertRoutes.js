const express = require("express");
const router = express.Router();
const { saveAlert, getAlerts } = require("../controllers/alertController");

router.post("/", saveAlert);
router.get("/", getAlerts);

module.exports = router;
