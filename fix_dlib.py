#!/usr/bin/env python3
"""
Fix dlib/face_recognition install.
Run: python fix_dlib.py (in venv)
"""

import subprocess
import sys

print("🔧 Installing dlib + face_recognition...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "dlib==19.24.4", "face-recognition==1.3.0", "--no-cache-dir", "--verbose"])

print("✅ Complete! Run 'python add_student_face.py' to register your face.")
