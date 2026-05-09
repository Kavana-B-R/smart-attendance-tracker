#!/usr/bin/env python3
"""
Smart Attendance Tracker - MongoDB Version
Run with: python run.py
"""

import os
from app import app

if __name__ == '__main__':
    print("🚀 Starting Smart Attendance Tracker (MongoDB)")
    print("Login: student1/student123 or teacher1/teacher123")
    app.run(debug=True, port=5000, host='0.0.0.0')

