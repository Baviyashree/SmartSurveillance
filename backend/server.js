const express = require("express");
const cors = require("cors");
require("dotenv").config();
const alertRoutes = require("./routes/alertRoutes");
const cameraRoutes = require("./routes/camera");

const app = express();
app.use(cors());
app.use(express.json());
app.use("/", cameraRoutes);

app.use("/api/alerts", alertRoutes);



app.listen(5000, () => {
  console.log(" Express backend running on port 5000");
});
