from flask import Flask, render_template, Response, jsonify
import cv2
import os
import threading
import time

app = Flask(__name__, template_folder='../templates')

# --- GLOBALS ---
camera = None
is_verified = False
scan_message = "B.U.D is scanning your face"
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TRAINER_PATH = os.path.join(PROJECT_ROOT, 'trainer.yml')

# Load the trained model
if os.path.exists(TRAINER_PATH):
    recognizer.read(TRAINER_PATH)
else:
    print(f"WARNING: No training data found at {TRAINER_PATH}! Run vision.py first.")

def generate_frames():
    global is_verified, camera, scan_message
    camera = cv2.VideoCapture(0)
    
    verified_frame_count = 0
    
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
                
            # 1. Face Recognition Logic
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
            
            if len(faces) == 0:
                scan_message = "B.U.D is scanning your face"

            for (x, y, w, h) in faces:
                # We DON'T draw rectangles here anymore! 
                # The HTML/CSS does the graphics. We just do the math.
                id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                
                # Confidence < 80 means it's you
                if confidence < 80:
                    verified_frame_count += 1
                    scan_message = "Verifying..."
                else:
                    verified_frame_count = max(0, verified_frame_count - 1)
                    scan_message = "Error , not my owner"
            

            # If we have 15 consistent frames of "You", we verify
            if verified_frame_count > 15:
                is_verified = True
                scan_message = "Done"

            # 2. Encode the frame to send to web browser
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
            if is_verified:
                # Keep streaming for a second so user sees the "Success" animation
                time.sleep(2)
                break
                
    except Exception as e:
        print(f"Camera Error: {e}")
        
    finally:
        camera.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/check_status')
def check_status():
    return jsonify({'verified': is_verified, 'message': scan_message})

def start_server():
    # Run Flask on port 5000
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    start_server()