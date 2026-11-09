from flask import Blueprint, Response, request, jsonify
import camera
from camera import generate_frames
from utils import save_alert_to_db, get_all_alerts   # ✅ import DB helpers

routes = Blueprint('routes', __name__)

# Mock database for camera locations (you can replace with actual DB)

# ------------------- CAMERA STREAM -------------------
@routes.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@routes.route('/video_feed/<int:camera_id>')
def video_feed_by_camera(camera_id):
    """Stream video from specific camera"""
    return Response(
        generate_frames(camera_id),  # Assuming generate_frames can accept camera_id
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# ------------------- START/STOP MODEL -------------------
@routes.route('/start-model', methods=['POST'])
def start_model():
    camera.running_model = True
    print("[DEBUG] Model started ✅")
    return jsonify({"status": "success", "message": "Model started"})

@routes.route('/stop-model', methods=['POST'])
def stop_model():
    camera.running_model = False
    print("[DEBUG] Model stopped ❌")
    return jsonify({"status": "success", "message": "Model stopped"})

@routes.route('/start-model/<int:camera_id>', methods=['POST'])
def start_model_for_camera(camera_id):
    """Start model for specific camera"""
    # Add logic to start model for specific camera
    return jsonify({
        "status": "success", 
        "message": f"Model started for camera {camera_id}",
        "camera_id": camera_id
    })

@routes.route('/stop-model/<int:camera_id>', methods=['POST'])
def stop_model_for_camera(camera_id):
    """Stop model for specific camera"""
    # Add logic to stop model for specific camera
    return jsonify({
        "status": "success", 
        "message": f"Model stopped for camera {camera_id}",
        "camera_id": camera_id
    })

# ------------------- CAMERA LOCATIONS MANAGEMENT -------------------
@routes.route('/camera-locations', methods=['GET'])
def get_camera_locations():
    """Get all camera locations"""
    # Optional filters
    status = request.args.get('status')  # ?status=active
    camera_type = request.args.get('type')  # ?type=entrance
    
    cameras = CAMERA_LOCATIONS.copy()
    
    # Apply filters
    if status:
        cameras = [cam for cam in cameras if cam['status'] == status]
    if camera_type:
        cameras = [cam for cam in cameras if cam['type'] == camera_type]
    
    return jsonify({
        "status": "success",
        "count": len(cameras),
        "cameras": cameras
    })

@routes.route('/camera-locations/<int:camera_id>', methods=['GET'])
def get_camera_location(camera_id):
    """Get specific camera location"""
    camera = next((cam for cam in CAMERA_LOCATIONS if cam['id'] == camera_id), None)
    
    if not camera:
        return jsonify({
            "status": "error",
            "message": "Camera not found"
        }), 404
    
    return jsonify({
        "status": "success",
        "camera": camera
    })

@routes.route('/camera-locations', methods=['POST'])
def add_camera_location():
    """Add new camera location"""
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    
    required_fields = ['name', 'lat', 'lng', 'type']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "status": "error", 
                "message": f"Missing required field: {field}"
            }), 400
    
    # Generate new ID
    new_id = max([cam['id'] for cam in CAMERA_LOCATIONS], default=0) + 1
    
    new_camera = {
        "id": new_id,
        "name": data['name'],
        "lat": data['lat'],
        "lng": data['lng'],
        "status": data.get('status', 'active'),
        "type": data['type']
    }
    
    CAMERA_LOCATIONS.append(new_camera)
    
    return jsonify({
        "status": "success",
        "message": "Camera location added",
        "camera": new_camera
    }), 201

@routes.route('/camera-locations/<int:camera_id>', methods=['PUT'])
def update_camera_location(camera_id):
    """Update camera location"""
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    
    camera_index = None
    for i, cam in enumerate(CAMERA_LOCATIONS):
        if cam['id'] == camera_id:
            camera_index = i
            break
    
    if camera_index is None:
        return jsonify({
            "status": "error",
            "message": "Camera not found"
        }), 404
    
    # Update camera data
    camera = CAMERA_LOCATIONS[camera_index]
    camera.update({
        key: value for key, value in data.items() 
        if key in ['name', 'lat', 'lng', 'status', 'type']
    })
    
    return jsonify({
        "status": "success",
        "message": "Camera location updated",
        "camera": camera
    })

@routes.route('/camera-locations/<int:camera_id>', methods=['DELETE'])
def delete_camera_location(camera_id):
    """Delete camera location"""
    camera_index = None
    for i, cam in enumerate(CAMERA_LOCATIONS):
        if cam['id'] == camera_id:
            camera_index = i
            break
    
    if camera_index is None:
        return jsonify({
            "status": "error",
            "message": "Camera not found"
        }), 404
    
    deleted_camera = CAMERA_LOCATIONS.pop(camera_index)
    
    return jsonify({
        "status": "success",
        "message": "Camera location deleted",
        "deleted_camera": deleted_camera
    })

@routes.route('/camera-locations/<int:camera_id>/status', methods=['PATCH'])
def update_camera_status(camera_id):
    """Update camera status (active/inactive/maintenance)"""
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({
            "status": "error", 
            "message": "Status field required"
        }), 400
    
    valid_statuses = ['active', 'inactive', 'maintenance']
    if data['status'] not in valid_statuses:
        return jsonify({
            "status": "error",
            "message": f"Invalid status. Must be one of: {valid_statuses}"
        }), 400
    
    camera = next((cam for cam in CAMERA_LOCATIONS if cam['id'] == camera_id), None)
    
    if not camera:
        return jsonify({
            "status": "error",
            "message": "Camera not found"
        }), 404
    
    camera['status'] = data['status']
    
    return jsonify({
        "status": "success",
        "message": f"Camera status updated to {data['status']}",
        "camera": camera
    })

# ------------------- CAMERA STATISTICS -------------------
@routes.route('/camera-stats', methods=['GET'])
def get_camera_stats():
    """Get camera statistics"""
    total_cameras = len(CAMERA_LOCATIONS)
    active_cameras = len([cam for cam in CAMERA_LOCATIONS if cam['status'] == 'active'])
    inactive_cameras = len([cam for cam in CAMERA_LOCATIONS if cam['status'] == 'inactive'])
    maintenance_cameras = len([cam for cam in CAMERA_LOCATIONS if cam['status'] == 'maintenance'])
    
    # Group by type
    camera_types = {}
    for cam in CAMERA_LOCATIONS:
        cam_type = cam['type']
        if cam_type not in camera_types:
            camera_types[cam_type] = 0
        camera_types[cam_type] += 1
    
    return jsonify({
        "status": "success",
        "stats": {
            "total": total_cameras,
            "active": active_cameras,
            "inactive": inactive_cameras,
            "maintenance": maintenance_cameras,
            "by_type": camera_types
        }
    })

# ------------------- ALERTS API -------------------
@routes.route('/api/alerts', methods=['POST'])
def receive_alert():
    """
    Endpoint to receive alerts and save them to the DB with camera location
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    try:
        camera_id = data.get("camera_id")
        message = data.get("message", "Alert detected")
        
        # Get camera location
        camera = next((cam for cam in CAMERA_LOCATIONS if cam['id'] == camera_id), None)
        lat, lng = None, None
        if camera:
            lat, lng = camera['lat'], camera['lng']

        # ✅ Save alert to DB with location
        save_alert_to_db(message, lat, lng)

        return jsonify({
            "status": "success", 
            "message": "Alert saved",
            "camera_location": {"lat": lat, "lng": lng} if camera else None
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@routes.route('/api/alerts', methods=['GET'])
def get_alerts():
    """
    Fetch all alerts from the database
    """
    try:
        alerts = get_all_alerts()
        
        # Convert to more readable format
        formatted_alerts = []
        for alert in alerts:
            formatted_alerts.append({
                "id": alert[0],
                "message": alert[1],
                "latitude": alert[2],
                "longitude": alert[3],
                "timestamp": alert[4]
            })
        
        return jsonify({
            "status": "success",
            "count": len(formatted_alerts),
            "alerts": formatted_alerts
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@routes.route('/api/alerts/<int:alert_id>', methods=['GET'])
def get_alert(alert_id):
    """Get specific alert"""
    try:
        alerts = get_all_alerts()
        alert = next((alert for alert in alerts if alert[0] == alert_id), None)
        
        if not alert:
            return jsonify({
                "status": "error",
                "message": "Alert not found"
            }), 404
        
        formatted_alert = {
            "id": alert[0],
            "message": alert[1],
            "latitude": alert[2],
            "longitude": alert[3],
            "timestamp": alert[4]
        }
        
        return jsonify({
            "status": "success",
            "alert": formatted_alert
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500