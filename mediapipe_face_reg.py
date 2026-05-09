import cv2
import mediapipe as mp
import numpy as np
import pickle
import base64
import mysql.connector
import os

print("🔥 MediaPipe Face Registration - No dlib needed!")

# MySQL config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'hemanth kumar G',
    'database': 'smart_attendance'
}

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Get student ID
student_id = input("Enter student ID (student1): ").strip() or "student1"

# Capture face
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("📸 Position face → Press SPACE to capture → ESC to skip")

with mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
) as face_mesh:
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Camera error")
            break
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image_rgb)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w, _ = image.shape
                # Key landmarks (nose, eyes, mouth)
                nose = face_landmarks.landmark[1]
                left_eye = face_landmarks.landmark[33]
                right_eye = face_landmarks.landmark[362]
                mouth = face_landmarks.landmark[13]
                
                # Create simple 128d "embedding" from normalized landmarks
                embedding = np.array([
                    nose.x, nose.y, nose.z,
                    left_eye.x, left_eye.y, left_eye.z,
                    right_eye.x, right_eye.y, right_eye.z,
                    mouth.x, mouth.y, mouth.z
                ] * 10)  # Pad to 120d, approx face_rec style
                
                embedding = embedding[:128]  # Exact 128d
                
                mp_drawing.draw_landmarks(
                    image, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION)
                
                cv2.putText(image, 'Press SPACE to save', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord(' '):  # SPACE
                    # Save embedding
                    enc_bytes = pickle.dumps(embedding)
                    enc_b64 = base64.b64encode(enc_bytes).decode()
                    
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET face_encoding = %s WHERE student_id = %s", (enc_b64, student_id))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    print(f"✅ Face saved for {student_id}")
                    cap.release()
                    cv2.destroyAllWindows()
                    break
                elif key == 27:  # ESC
                    break
        else:
            cv2.putText(image, 'No face - adjust position', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        
        cv2.imshow('MediaPipe Face Registration', image)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()

print("Done! Test with check_faces.py")

