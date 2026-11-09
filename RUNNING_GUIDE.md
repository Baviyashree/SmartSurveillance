# Smart Surveillance Project: Overview and Run Guide

## What this project does

Smart Surveillance is a prototype that combines computer vision with a web dashboard to help identify possible distress:

1. The Python application reads video from the computer's webcam.
2. Its AI code checks facial expressions and, when a distress-related emotion continues, analyzes frames for silent lip-read keywords such as **Help**, **Danger**, **No**, **Please**, and **Stop**.
3. When it detects a possible alert, it stores alert information locally and sends it to the Node.js backend.
4. The backend stores alerts and camera locations in MySQL. It can also send an SMS to the configured rescue-team phone using Twilio.
5. The React frontend displays the live camera feed, recent alerts, and camera locations on an Azure Maps map.

This is an assistance prototype, not a replacement for emergency services or human review. Camera access, the trained model file, database setup, and external service credentials are required for all features to work.

## How the project folders fit together

The project has three parts. Run each part in its own terminal window and leave all three running:

| Part              | Folder          | Purpose                                                               | Default port |
| ----------------- | --------------- | --------------------------------------------------------------------- | ------------ |
| Python AI service | `pythonProject` | Webcam video, emotion/lip-reading processing, and local alert storage | `9000`       |
| Node.js backend   | `backend`       | Alert and camera APIs, MySQL access, and Twilio SMS notifications     | `5000`       |
| React frontend    | `frontend`      | User dashboard, live feed, alerts, and map                            | `3000`       |

The frontend talks to both services: it uses the Python service for the live feed and the Node.js backend for alerts and camera locations.

## 1. Python project

### What `pythonProject` contains

- `app.py` starts the Flask application on port `9000` and initializes the local SQLite database.
- `routes.py` defines endpoints for the video feed, starting and stopping the model, camera locations, and other camera operations.
- `camera.py` reads frames from the default webcam (camera index `0`) and provides the video stream.
- `main.py` analyzes video frames using facial-emotion and lip-reading models.
- `alerts.py` defines Flask endpoints for reading and saving alerts.
- `utils.py` creates and uses the SQLite database (`alerts2.db`) and forwards alerts to the Node.js backend.
- `requirements.txt` lists Python packages needed by the application.
- `alerts.db`, `alerts1.db`, and `alerts2.db` are SQLite database files; `alerts2.db` is the database initialized by the current application.
- `python\` contains another copy of several Python files. The commands below run the files directly in `pythonProject`, not the copies inside `pythonProject\python\`.

### Before running

- Install Python and make sure `python --version` reports a version compatible with the project's TensorFlow and computer-vision packages.
- Allow the application to use your webcam.
- The lip-reading model file is loaded from this path in `main.py`:
  `<your-path>\distress_keyword_model1 (1).h5`
  Make sure the file exists there, or update the model path in `pythonProject\main.py` to its actual location. This model file is not in the `pythonProject` folder.

### Install Python requirements and start the application

Open **Command Prompt** in the project root, then run:

```bat
cd C:\<your-path>\pythonProject
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If you are using **PowerShell**, run the same commands but replace `venv\Scripts\activate` with:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, use Command Prompt and run `venv\Scripts\activate` there instead.

When the server starts, keep this terminal open. The Python service listens on port `9000`. The dashboard uses its `/start-model`, `/stop-model`, and `/video_feed` endpoints.

## 2. Backend

### What `backend` contains

- `server.js` starts the Express API on port `5000`.
- `routes\alertRoutes.js` and `controllers\alertController.js` provide alert endpoints and handle saving alerts and requesting Twilio SMS notifications.
- `routes\camera.js` provides camera-location data.
- `db\db.js` creates the MySQL connection.
- `package.json` and `package-lock.json` describe and lock the Node.js dependencies.
- `.env` is used for Twilio configuration. Keep its credentials private.

### Before running

- Install Node.js and npm.
- Start and configure a local MySQL server. The backend is configured to connect to <your-local> database on `localhost`update `backend\db\db.js` of your MySQL connection settings.
- Create the MySQL tables expected by the code. The backend uses an `alerts2` table with `camera_id`, `keyword`, `emotion`, `lat`, `lng`, and `timestamp` columns, and a `cameras` table with `camera_id`, `lat`, and `lng` columns.
- To send SMS notifications, configure these variables in `backend\.env`: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE`, and `RESCUE_TEAM_PHONE`. Use valid values from your Twilio account; do not share or commit them.

### Install backend packages and start the server

Open a **new terminal** so the Python application can keep running, then run:

```bat
cd C:\<your-path>\backend
npm install
node server.js
```

`npm install` downloads the backend packages into `backend\node_modules`. The backend's `package.json` does not define an `npm start` script or include Nodemon, so `node server.js` is the standard start command. If Nodemon is already installed on your computer, you can instead run:

```bat
nodemon server.js
```

Keep the backend terminal open. The API listens on port `5000`.

## 3. Frontend

### What `frontend` contains

- `src\App.js` is the React application entry component.
- `src\components\Dashboardog.js` displays the live camera feed, recent alerts, camera markers, and Azure Maps map.
- `src\components\Alerts.js`, `Navbar.js`, and related files provide dashboard components and styling.
- `public\` contains the HTML page and static assets.
- `package.json` and `package-lock.json` define the React application and its dependencies.
- `.env` provides the Azure Maps configuration. The dashboard reads `REACT_APP_AZURE_MAPS_KEY`; set it to a valid Azure Maps key for the map to load, and keep the key private.

### Install frontend packages and start the website

Open another **new terminal**, then run:

```bat
cd C:\<your-path>\frontend
npm install
npm start
```

`npm install` downloads the frontend packages into `frontend\node_modules`. `npm start` launches the React development server. If you change the Azure Maps key in `.env`, stop and restart the frontend.

## Accessing the frontend

After the frontend starts, open **http://localhost:3000** in your browser. The development server may offer another port if port `3000` is already in use.

## 4. Set up your own MySQL database

The Node.js backend needs a MySQL database for alerts and camera locations. You can use MySQL Workbench or the MySQL command line:

1. Install and start MySQL Server, then connect to it using an administrator account.
2. Choose your own database name, MySQL username, and strong password. In the SQL below, replace `smart_surveillance`, `surveillance_app`, and `ChooseA_StrongPassword` with your choices. Run the statements in MySQL Workbench or the MySQL command line:

```sql
CREATE DATABASE smart_surveillance;
CREATE USER 'surveillance_app'@'localhost'
  IDENTIFIED BY 'ChooseA_StrongPassword';
GRANT ALL PRIVILEGES ON smart_surveillance.* TO 'surveillance_app'@'localhost';

USE smart_surveillance;

CREATE TABLE alerts2 (
  id INT AUTO_INCREMENT PRIMARY KEY,
  camera_id VARCHAR(50) NOT NULL,
  keyword VARCHAR(10) NOT NULL,
  emotion VARCHAR(50),
  lat DECIMAL(10, 7),
  lng DECIMAL(10, 7),
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cameras (
  camera_id VARCHAR(50) PRIMARY KEY,
  lat DECIMAL(10, 7) NOT NULL,
  lng DECIMAL(10, 7) NOT NULL
);

INSERT INTO cameras (camera_id, lat, lng) VALUES
  ('cam01', 13.0827000, 80.2707000),
  ('cam02', 13.0850000, 80.2740000),
  ('cam03', 13.0800000, 80.2680000),
  ('cam04', 13.0835000, 80.2720000);
```

3. Configure the backend to use your MySQL server. In `backend\db\db.js`, set `host`, `user`, `password`, and `database` in the connection configuration to your MySQL host, username, password, and database name. For a local MySQL server, the host is often `localhost`. The account created above is limited to connections from `localhost`; if MySQL is on another machine, create an account permitted from the backend machine and configure the server's network access securely.
4. Save the changes and restart the backend. The backend needs to be able to connect to MySQL before it can read camera locations or save alerts.

Keep your MySQL password private. Do not publish it in this guide or commit it to a public repository.

## 5. Twilio account setup (SMS alerts)

The backend uses Twilio to send an SMS when it saves an alert. The current backend initializes its Twilio client when it starts, so configure valid Twilio credentials before running the backend, even if you are only testing the dashboard.

1. Create a Twilio account and obtain an SMS-capable Twilio phone number.
2. From the Twilio Console, copy the Account SID and Auth Token. Set the verified rescue-team phone number that should receive alerts.
3. Put these values in `backend\.env`, replacing the placeholders with your own values:

```dotenv
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE=your_twilio_phone_number
RESCUE_TEAM_PHONE=your_rescue_team_phone_number
```

Use the full international phone-number format (for example, `+1...`) and follow Twilio's account requirements. Trial accounts may only send messages to verified recipient numbers. Keep the Auth Token secret and never commit real credentials.

## 6. Azure Maps setup

The frontend uses Azure Maps to display camera locations. To enable the map:

1. Create or sign in to an Azure account and create an **Azure Maps** account/resource in the Azure portal.
2. Copy an Azure Maps subscription key from the resource's authentication settings.
3. Set the key in `frontend\.env`:

```dotenv
REACT_APP_AZURE_MAPS_KEY=your_azure_maps_subscription_key
```

4. Save the file and restart the frontend with `npm start`. The map will use the key to load; without it, the rest of the dashboard may still open, but the map will not initialize.

Treat the key as sensitive: do not publish it or commit a real key to a public repository. Since this React app uses the key in the browser, follow Azure Maps guidance for securing and restricting keys, and rotate the key if it is exposed.
