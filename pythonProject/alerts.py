from flask import Blueprint, jsonify, request
from utils import (
    get_all_alerts,
    get_alerts_by_camera,
    save_alert_to_db,
    get_recent_alerts,
    get_yes_no_alerts
)

alerts_bp = Blueprint("alerts", __name__)

# ✅ Get all alerts
@alerts_bp.route("/alerts", methods=["GET"])
def fetch_alerts():
    alerts = get_all_alerts()
    return jsonify(alerts), 200

# ✅ Get alerts by camera ID
@alerts_bp.route("/alerts/<camera_id>", methods=["GET"])
def fetch_alerts_by_camera(camera_id):
    alerts = get_alerts_by_camera(camera_id)
    return jsonify(alerts), 200

# ✅ Add new alert
@alerts_bp.route("/alerts", methods=["POST"])
def create_alert():
    data = request.json
    camera_id = data.get("camera_id")
    keyword = data.get("keyword")
    emotion = data.get("emotion")

    if not camera_id or not keyword:
        return jsonify({"error": "camera_id and keyword are required"}), 400

    save_alert_to_db(camera_id, keyword, emotion)
    return jsonify({"message": "Alert saved successfully"}), 201

# ✅ Get recent alerts
@alerts_bp.route("/alerts/recent/<int:limit>", methods=["GET"])
def fetch_recent_alerts(limit):
    alerts = get_recent_alerts(limit)
    return jsonify(alerts), 200

# ✅ Get only yes/no keyword alerts
@alerts_bp.route("/alerts/yesno", methods=["GET"])
def fetch_yes_no_alerts():
    alerts = get_yes_no_alerts()
    return jsonify(alerts), 200
