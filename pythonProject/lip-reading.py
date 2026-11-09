import cv2
from fer import FER
from keras.models import load_model
import numpy as np
import time
import requests
from datetime import datetime


# Load models
emotion_detector = FER(mtcnn=True)
lip_model = load_model(r"C:\Users\hp\Desktop\GJ_Square\Surveillance\fastapi\distress_keyword_model1 (1).h5")
classes = ['Danger', 'Help', 'No', 'Please', 'Stop']  

# Constants
FRAMES_PER_CLIP = 30
IMG_HEIGHT, IMG_WIDTH = 64, 128
DISTRESS_KEYWORDS = ['danger', 'help', 'no', 'please', 'stop']  

# Frame buffer
clip_frames = []

# Emotion state tracker
trigger_emotions = ['fear', 'angry', 'sad', 'neutral']
emotion_start_time = None
current_emotion = None
trigger = False

cap = cv2.VideoCapture(0)
def send_alert(camera_id, keyword, emotion):
    payload = {
        "camera_id": camera_id,
        "keyword": keyword,
        "emotion": emotion,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    try:
        res = requests.post("http://localhost:5000/api/alerts", json=payload)
        if res.ok:
            print("Alert sent to backend")
        else:
            print(" Failed to send alert:", res.status_code)
    except Exception as e:
        print("⚠️ Error while sending alert:", e)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    trigger = False  

    emotions = emotion_detector.detect_emotions(frame)

   
    for face in emotions:
        (x, y, w, h) = face["box"]
        emotion_scores = face["emotions"]
        top_emotion = max(emotion_scores, key=emotion_scores.get)

        
        if top_emotion.lower() in trigger_emotions:
            color = (0, 0, 255)  
        else:
            color = (0, 255, 0)  

        
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, f"{top_emotion} ({emotion_scores[top_emotion]:.2f})",
                    (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        
        emotion = top_emotion.lower()
        if emotion in trigger_emotions:
            if current_emotion != emotion:
                current_emotion = emotion
                emotion_start_time = time.time()
            else:
                duration = time.time() - emotion_start_time
                if duration >= 3:
                    trigger = True
        else:
            current_emotion = None
            emotion_start_time = None

    
    if trigger:
        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 10)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (IMG_WIDTH, IMG_HEIGHT))
        normalized = resized.astype("float32") / 255.0
        clip_frames.append(normalized)

        if len(clip_frames) == FRAMES_PER_CLIP:
            clip_np = np.array(clip_frames).reshape(1, FRAMES_PER_CLIP, IMG_HEIGHT, IMG_WIDTH, 1)
            preds = lip_model.predict(clip_np)
            keyword = classes[np.argmax(preds)]

            if keyword.lower() in DISTRESS_KEYWORDS:
                print("Alert- DISTRESS KEYWORD DETECTED")
                send_alert(camera_id="cam02", keyword="yes", emotion=current_emotion)
            # else:
            #     send_alert(camera_id="cam02", keyword="no", emotion=current_emotion)

            clip_frames = []  
    else:
        
        clip_frames = []

    
    cv2.imshow("Live Emotion + Lip Reading", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

