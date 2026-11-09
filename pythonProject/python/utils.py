import sqlite3

# Initialize DB with proper alert structure
def init_db():
    conn = sqlite3.connect("alerts2.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT,
            keyword TEXT CHECK (keyword IN ('yes','no')),
            emotion TEXT,
            latitude REAL,
            longitude REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Camera locations mapping
CAMERA_LOCATIONS = {
    "cam01": {"lat": 13.0827, "lng": 80.2707, "name": "Main Entrance"},
    "cam02": {"lat": 13.0850, "lng": 80.2740, "name": "Parking Lot A"},
    "cam03": {"lat": 13.0800, "lng": 80.2680, "name": "Emergency Exit"},
    "cam04": {"lat": 13.0835, "lng": 80.2720, "name": "Reception Area"},
}

# Save alert with camera location lookup
def save_alert_to_db(camera_id: str, keyword: str = None, emotion: str = None):
    # Map location
    if not camera_id:
        camera_id="unknown"
    else:
        camera_id = camera_id.strip().lower()
    location = CAMERA_LOCATIONS.get(camera_id, {})
    latitude = location.get("lat")
    longitude = location.get("lng")

    # ✅ Normalize keyword for DB constraint
    keyword = "yes" if keyword and keyword.lower() == "danger" else "no"

    # ---- Local backup in SQLite ----
    conn = sqlite3.connect("alerts2.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts2 (camera_id, keyword, emotion, latitude, longitude) 
        VALUES (?, ?, ?, ?, ?)
    """, (camera_id, keyword, emotion, latitude, longitude))
    conn.commit()
    conn.close()

    # ---- Send to Node backend ----
    alert_data = {
        "camera_id": camera_id,
        "keyword": keyword,
        "lat": latitude,
        "lng": longitude,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        res = requests.post("http://localhost:5000/api/alerts", json=alert_data)
        print("✅ Alert sent to backend:", res.json())
    except Exception as e:
        print("❌ Failed to send alert to backend:", str(e))
    # print(f"[DB] Alert saved: Camera={camera_id}, Keyword="{keyword}" , Emotion={emotion}, Location=({latitude}, {longitude})")

# Save simple alert with unknown camera
def save_simple_alert(message: str, emotion: str, latitude: float = None, longitude: float = None):
    conn = sqlite3.connect("alerts2.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts2 (camera_id, keyword, emotion, latitude, longitude) 
        VALUES (?, ?, ?, ?, ?)
    """, ("unknown", message, emotion, latitude, longitude))
    conn.commit()
    conn.close()

# Get all alerts
def get_all_alerts():
    conn = sqlite3.connect("alerts2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts2 ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Get alerts by camera
def get_alerts_by_camera(camera_id: str):
    conn = sqlite3.connect("alerts2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts2 WHERE camera_id = ? ORDER BY timestamp DESC", (camera_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Get recent alerts (last N alerts)
def get_recent_alerts(limit: int = 10):
    conn = sqlite3.connect("alerts2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts2 ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Delete old alerts (older than N days)
def cleanup_old_alerts(days: int = 30):
    conn = sqlite3.connect("alerts2.db")
    cursor = conn.cursor()
    cursor.execute(f"""
        DELETE FROM alerts2 
        WHERE timestamp < datetime('now', '-{days} days')
    """)
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"[DB] Cleaned up {deleted_count} old alerts")
    return deleted_count

# Get alerts where keyword is 'yes' or 'no'
def get_yes_no_alerts():
    conn = sqlite3.connect("alerts2.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM alerts2 
        WHERE keyword IN ('yes', 'no') 
        ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# Example usage and testing
if __name__ == "__main__":
    # Initialize the database
    init_db()

    # Save a test alert
    # save_alert_to_db("cam02", keyword="yes", emotion="neutral")

    # Get and print all alerts
    alerts = get_all_alerts()
    print("\nAll Alerts:")
    for alert in alerts2:
        print(f"ID: {alert[0]}, Camera: {alert[1]}, Keyword: {alert[2]}, Emotion: {alert[3]}, "
              f"Location: ({alert[4]}, {alert[5]}), Time: {alert[6]}")

    # Get and print alerts with keyword 'yes' or 'no'
    yes_no_alerts = get_yes_no_alerts()
    print("\nFiltered Alerts (Keyword = yes/no):")
