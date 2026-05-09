#!/usr/bin/env python3
"""
Check face encodings in MySQL users table.
Run: python check_faces.py
"""

import mysql.connector
import base64
import pickle

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'hemanth kumar G',
    'database': 'smart_attendance'
}

def check_faces():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT student_id, username, name, face_encoding FROM users WHERE role = 'student'")
    students = cursor.fetchall()
    
    print("👥 Student Faces:")
    print("-" * 60)
    
    for student in students:
        sid = student['student_id']
        name = student['name']
        enc = student['face_encoding']
        
        if enc:
            print(f"✅ {sid} ({name}): HAS face encoding ({len(enc)} chars)")
        else:
            print(f"❌ {sid} ({name}): NO face encoding")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_faces()

