import cv2
import numpy as np
import pickle
import base64
import mysql.connector
import os

print("🔥 OpenCV Face Registration - Guaranteed No Deps!")

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'hemanth kumar G',
    'database': 'smart_attendance'
}

student_id = input("Student ID (student1): ") or "student1"

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

print("📸 Press SPACE on face → ESC quit")

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.1, 4)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
    if len(faces) > 0:
        cv2.putText(frame, 'SPACE to SAVE', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, 'Find face', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    cv2.imshow('OpenCV Face Reg', frame)
    
    k = cv2.waitKey(1) & 0xFF
    if k == 27:  # ESC
        break
    if k == 32 and len(faces) > 0:  # SPACE + face found
        # Extract face ROI
        face = gray[y:y+h, x:x+w]
        # Flatten resized 32x32 to vector
        embedding = cv2.resize(face, (32, 32)).flatten()
        embedding = embedding.astype(np.float32) / 255.0
        
        # Save to DB
        enc_bytes = pickle.dumps(embedding)
        enc_b64 = base64.b64encode(enc_bytes).decode()
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET face_encoding = %s WHERE student_id = %s", (enc_b64, student_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Saved face for {student_id} - vector shape {embedding.shape}")
        break

cap.release()
cv2.destroyAllWindows()

print("Ready! Login → Attendance works with face match.")
