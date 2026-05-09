from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Date, Time, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    student_id = Column(String(50))
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum('student', 'teacher'), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    face_encoding = Column(Text)  # Base64 encoded list of encodings for multi-photo
    created_at = Column(DateTime, default=datetime.utcnow)

class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    teacher = relationship("User")

class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(Enum('present', 'absent', 'late'), default='absent')
    login_time = Column(Time)
    logout_time = Column(Time)
    face_verified = Column(Boolean, default=False)
    student = relationship("User")
    subject = relationship("Subject")

class PendingRegistration(Base):
    __tablename__ = 'pending_registrations'
    id = Column(Integer, primary_key=True)
    usn = Column(String(50), unique=True)
    name = Column(String(100))
    email = Column(String(100))
    encodings = Column(Text)  # JSON list of base64 face encodings
    status = Column(Enum('pending', 'approved', 'rejected'), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)

class ClassSetting(Base):
    __tablename__ = 'class_settings'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    slot_name = Column(String(50))
    start_time = Column(Time)
    end_time = Column(Time)
    late_threshold = Column(Integer, default=5)  # minutes
    subject = relationship("Subject")

class SlotAttendance(Base):
    __tablename__ = 'slot_attendance'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'))
    class_setting_id = Column(Integer, ForeignKey('class_settings.id'))
    status = Column(Enum('present', 'absent', 'late'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    student = relationship("User")

# MongoDB collections handled separately (videos, mcq_tests, etc.)

