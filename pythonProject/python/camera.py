import cv2
from main import process_frame

camera = cv2.VideoCapture(0)
running_model = False


def generate_frames():
    global running_model
    while True:
        success, frame = camera.read()
        if not success:
            break

        if running_model:

            frame = process_frame(frame)


        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
