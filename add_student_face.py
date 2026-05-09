#!/usr/bin/env python3
"""
Add face encoding to student1 for face recognition testing.
Run: python add_student_face.py
Requires camera access.
"""

import mysql.connector
import cv2
import numpy as np
import face_recognition
import base64
import pickle
from io import BytesIO

# DB config from app.py
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'hemanth kumar G',
    'database': 'smart_attendance'
}

def capture_face():
    """Capture and encode face from webcam."""
    cap = cv2.VideoCapture(0)
    print("📸 Look at camera. Press SPACE to capture, ESC to exit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Show preview
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        # Draw rectangle
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        cv2.imshow('Capture Face for Student1', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACE
            if face_locations:
                face_enc = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                cap.release()
                cv2.destroyAllWindows()
                print("✅ Face captured!")
                return face_enc
            else:
                print("❌ No face detected. Try again.")
        elif key == 27:  # ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return None

def save_to_db(face_enc):
    """Save encoding to student1 user."""
    # Base64 encode
    enc_bytes = pickle.dumps(face_enc)
    enc_b64 = base64.b64encode(enc_bytes).decode()
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Update student1
    cursor.execute("""
        UPDATE users SET face_encoding = %s WHERE student_id = 'student1'
    """, (enc_b64,))
    
    if cursor.rowcount > 0:
        print("✅ Face encoding saved for student1!")
    else:
        print("❌ student1 not found. Run python init_db.py first.")
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    print("🎭 Face Registration for Student1")
    face_enc = capture_face()
    if face_enc is not None:
        save_to_db(face_enc)
        print("\n🎉 Ready! Login student1/student123 → Attendance → Mark Attendance")
    else:
        print("❌ No face captured.")

