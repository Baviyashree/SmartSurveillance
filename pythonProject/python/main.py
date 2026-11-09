import time
import numpy as np
import cv2
from fer import FER
from keras.models import load_model
from utils import save_alert_to_db
import requests
# Load models
emotion_detector = FER(mtcnn=True)
lip_model = load_model(r"C:\\<your-path>\\distress_keyword_model1 (1).h5")
classes = ['Danger', 'Help', 'No', 'Please', 'Stop']

# Constants
FRAMES_PER_CLIP = 30
IMG_HEIGHT, IMG_WIDTH = 64, 128
DISTRESS_KEYWORDS = ['danger', 'help', 'no', 'please', 'stop']
trigger_emotions = ['fear', 'angry', 'sad', 'neutral']

# State variables
clip_frames = []
emotion_start_time = None
current_emotion = None
trigger = False


def process_frame(frame):
    """Run emotion + lip-reading detection on a frame and draw alerts."""
    global emotion_start_time, current_emotion, trigger, clip_frames

    emotions = emotion_detector.detect_emotions(frame)
    trigger = False

    for face in emotions:
        (x, y, w, h) = face["box"]
        emotion_scores = face["emotions"]
        top_emotion = max(emotion_scores, key=emotion_scores.get)

        # Color based on emotion
        if top_emotion.lower() in trigger_emotions:
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)

        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, f"{top_emotion} ({emotion_scores[top_emotion]:.2f})",
                    (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # Emotion tracking for trigger
        emotion = top_emotion.lower()
        if emotion in trigger_emotions:
            if current_emotion != emotion:
                current_emotion = emotion
                emotion_start_time = time.time()
            else:
                if time.time() - emotion_start_time >= 3:
                    trigger = True
        else:
            current_emotion = None
            emotion_start_time = None

    # If distress detected after 3s
    if trigger:
        # Draw big outer red bounding box
        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 10)

        # Prepare lip-reading frames
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (IMG_WIDTH, IMG_HEIGHT))
        normalized = resized.astype("float32") / 255.0
        clip_frames.append(normalized)

        # Run keyword prediction
        if len(clip_frames) == FRAMES_PER_CLIP:
            clip_np = np.array(clip_frames).reshape(1, FRAMES_PER_CLIP, IMG_HEIGHT, IMG_WIDTH, 1)
            preds = lip_model.predict(clip_np)
            keyword = classes[np.argmax(preds)]

  # add at the top

            if keyword.lower() in DISTRESS_KEYWORDS:
                try:
                    # save_alert_to_db(camera_id="cam02", keyword=keyword, emotion=current_emotion)
                    response = requests.post("http://localhost:5000/api/alerts", json={
                    "camera_id": "cam02",
                    "keyword": keyword,
                    "emotion": current_emotion
                    })
                    print("✅ Alert sent to backend:", response.json())
                except Exception as e:
                    print("❌ Failed to send alert:", e)

            else:
        # Reset frame buffer if no trigger
                clip_frames.clear()

    return frame
