# Face Recognition Attendance System MVP

## Quick Start (Windows)

1. **Install Dependencies**
```
pip install -r requirements.txt
```

2. **Initialize SQLite Database** (uses models.py)
```
python -c "from models import init_models; init_models('sqlite:///attendance.db')"
```

3. **Start Backend**
```
python app.py
```

4. **Test in Browser**
- http://127.0.0.1:5000
- Student: student1 / student123
- Teacher: teacher1 / teacher123

5. **Face Registration** (first time)
```
python add_student_face.py
```

## Features Implemented
- ✅ USN Login (Student/Teacher)
- ✅ Face Recognition Attendance (OpenCV + face_recognition)
- ✅ Multi-class support ready (models)
- ✅ Video Management
- ✅ MCQ Tests
- ✅ Dashboards with analytics base

## Flutter Mobile (Next)
```
mkdir flutter_attendance
cd flutter_attendance
flutter create .
flutter pub add http image_picker shared_preferences intl provider
```

## Database
- Primary: SQLite (`attendance.db`)
- Models: `models.py` (SQLAlchemy ORM)
- Schema: Full spec match + approvals/slots

## Run Commands
| Action | Command |
|--------|---------|
| Backend | `python app.py` |
| Init DB | `python -c "from models import init_models"` |
| Face Reg | `python add_student_face.py` |
| Test App | http://127.0.0.1:5000 |

**MVP Status: Backend Ready. Mobile pending.**

