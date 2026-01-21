import cv2
import os
import numpy as np
import math

# --- PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(PROJECT_ROOT, "face_data")

# Create a folder to store your face data
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

# --- COLORS (BGR Format) ---
CYAN = (255, 255, 0)   # Note: OpenCV uses BGR, so this is Cyan
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)

def draw_corner_rect(img, bbox, color, thickness=2, length=30):
    """
    Draws the 'Face ID' style bracket corners.
    bbox: (x, y, w, h)
    """
    x, y, w, h = bbox
    
    # Top Left
    cv2.line(img, (x, y), (x + length, y), color, thickness)
    cv2.line(img, (x, y), (x, y + length), color, thickness)
    
    # Top Right
    cv2.line(img, (x + w, y), (x + w - length, y), color, thickness)
    cv2.line(img, (x + w, y), (x + w, y + length), color, thickness)
    
    # Bottom Left
    cv2.line(img, (x, y + h), (x + length, y + h), color, thickness)
    cv2.line(img, (x, y + h), (x, y + h - length), color, thickness)
    
    # Bottom Right
    cv2.line(img, (x + w, y + h), (x + w - length, y + h), color, thickness)
    cv2.line(img, (x + w, y + h), (x + w, y + h - length), color, thickness)

def train_face():
    cam = cv2.VideoCapture(0)
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    print("\n[TRAINING] Look at the camera...")
    
    count = 0
    while True:
        ret, img = cam.read()
        if not ret: break
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:
            # Draw the simple training box
            draw_corner_rect(img, (x,y,w,h), CYAN, 3)
            count += 1
            cv2.imwrite(f"{DATA_PATH}/User.{count}.jpg", gray[y:y+h,x:x+w])
            cv2.imshow('Training', img)

        if cv2.waitKey(100) & 0xFF == ord('q'): break
        elif count >= 30: break

    cam.release()
    cv2.destroyAllWindows()
    
    print("[TRAINING] Compiling data...")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces = []
    ids = []
    
    image_paths = [os.path.join(DATA_PATH, f) for f in os.listdir(DATA_PATH)]
    for path in image_paths:
        img_numpy = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        faces.append(img_numpy)
        ids.append(1) 

    recognizer.train(faces, np.array(ids))
    TRAINER_PATH = os.path.join(PROJECT_ROOT, 'trainer.yml')
    recognizer.write(TRAINER_PATH)
    print(f"[TRAINING] Complete. Saved to {TRAINER_PATH}")

def scan_face():
    TRAINER_PATH = os.path.join(PROJECT_ROOT, 'trainer.yml')
    if not os.path.exists(TRAINER_PATH):
        print(f"Error: No training data found at {TRAINER_PATH}")
        return False

    print("\n[SECURITY] Starting Face ID Scan...")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(TRAINER_PATH)
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cam = cv2.VideoCapture(0)
    
    angle = 0  # For the rotating radar
    recognized_frames = 0
    
    # Run for approx 4 seconds (120 frames)
    for _ in range(120):
        ret, img = cam.read()
        if not ret: break
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.2, 5)
        
        # UI: Draw a dark overlay for contrast (optional, makes it look cooler)
        # img = cv2.addWeighted(img, 0.8, np.zeros_like(img), 0.2, 0)

        # UI: Center Crosshair
        height, width, _ = img.shape
        cx, cy = width // 2, height // 2
        # Faint center cross
        cv2.line(img, (cx - 20, cy), (cx + 20, cy), (100, 100, 100), 1)
        cv2.line(img, (cx, cy - 20), (cx, cy + 20), (100, 100, 100), 1)

        for (x,y,w,h) in faces:
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
            
            # --- ANIMATION CALCULATIONS ---
            # Center of the face
            center_x = x + w // 2
            center_y = y + h // 2
            radius = int(w / 1.5)
            
            if confidence < 85: # Verified
                recognized_frames += 1
                color = GREEN
                status = "UNLOCKED"
                # Draw full solid circle when verified
                cv2.circle(img, (center_x, center_y), radius, GREEN, 2)
            else: # Scanning / Unknown
                color = CYAN
                status = "SCANNING..."
                
                # Draw the ROTATING ARCS (The "Loading" effect)
                angle += 10
                if angle >= 360: angle = 0
                
                # Arc 1
                cv2.ellipse(img, (center_x, center_y), (radius, radius), angle, 0, 60, CYAN, 2)
                # Arc 2 (Opposite)
                cv2.ellipse(img, (center_x, center_y), (radius, radius), angle + 180, 0, 60, CYAN, 2)
                # Arc 3 (Inner fast ring)
                cv2.ellipse(img, (center_x, center_y), (radius - 20, radius - 20), -angle * 2, 0, 40, WHITE, 1)

            # --- DRAW THE BRACKETS (Like the image) ---
            # We draw a black shadow first for the "glitch/3D" look, then the color
            draw_corner_rect(img, (x+2, y+2, w, h), BLACK, thickness=3) 
            draw_corner_rect(img, (x, y, w, h), color, thickness=2)

            # Text Label
            cv2.putText(img, status, (x + 5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow('Face ID', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

    if recognized_frames > 20:
        return True
    else:
        return False

if __name__ == "__main__":
    scan_face()