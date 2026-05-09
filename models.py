from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Time, Boolean, DateTime, ForeignKey, Enum, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.mysql import TIMESTAMP as MySQLTimestamp
from datetime import datetime
import enum

Base = declarative_base()

# Enums
class RoleEnum(enum.Enum):
    student = 'student'
    teacher = 'teacher'

class StatusEnum(enum.Enum):
    present = 'present'
    absent = 'absent'
    late = 'late'

# Core Tables (from database.sql + spec additions)
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    student_id = Column(String(50))
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    face_encoding = Column(Text)  # Base64 pickled list of encodings
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    attendances = relationship('Attendance', back_populates='student')
    subjects_taught = relationship('Subject', foreign_keys='Subject.teacher_id')

class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    teacher = relationship('User', foreign_keys=[teacher_id])
    attendances = relationship('Attendance', back_populates='subject')

class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(Enum(StatusEnum), default='absent')
    login_time = Column(Time)
    logout_time = Column(Time)
    face_verified = Column(Boolean, default=False)
    
    # Relationships
    student = relationship('User', back_populates='attendances')
    subject = relationship('Subject', back_populates='attendances')

class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    filename = Column(String(255), nullable=False)
    topic = Column(String(100))
    upload_date = Column(TIMESTAMP, default=datetime.utcnow)
    duration = Column(Integer, default=0)

class VideoView(Base):
    __tablename__ = 'video_views'
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    watch_duration = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    view_date = Column(TIMESTAMP, default=datetime.utcnow)

class McqTest(Base):
    __tablename__ = 'mcq_tests'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    title = Column(String(200), nullable=False)
    topic = Column(String(100), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    questions = relationship('McqQuestion', back_populates='test')

class McqQuestion(Base):
    __tablename__ = 'mcq_questions'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('mcq_tests.id'), nullable=False)
    question = Column(Text, nullable=False)
    option_a = Column(String(255), nullable=False)
    option_b = Column(String(255), nullable=False)
    option_c = Column(String(255), nullable=False)
    option_d = Column(String(255), nullable=False)
    correct_answer = Column(String(1), nullable=False)
    
    test = relationship('McqTest', back_populates='questions')

class TestResult(Base):
    __tablename__ = 'test_results'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('mcq_tests.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    attempted_at = Column(TIMESTAMP, default=datetime.utcnow)

class ActivityLog(Base):
    __tablename__ = 'activity_log'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    activity_type = Column(String(50), nullable=False)
    details = Column(Text)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)

class ScreenTime(Base):
    __tablename__ = 'screen_time'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    login_time = Column(TIMESTAMP, default=datetime.utcnow)
    logout_time = Column(TIMESTAMP)
    total_seconds = Column(Integer, default=0)

# Live Class (new)
class LiveClass(Base):
    __tablename__ = 'live_classes'
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    class_code = Column(String(10), unique=True)  # Room code for join
    started_at = Column(TIMESTAMP)
    ended_at = Column(TIMESTAMP)
    max_students = Column(Integer, default=10)
    active = Column(Boolean, default=False)
    title = Column(String(200))

class LiveClassAttendance(Base):
    __tablename__ = 'live_class_attendance'
    id = Column(Integer, primary_key=True)
    live_class_id = Column(Integer, ForeignKey('live_classes.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    joined_at = Column(TIMESTAMP, default=datetime.utcnow)
    left_at = Column(TIMESTAMP)

# Spec Additions for MVP
class PendingRegistration(Base):
    __tablename__ = 'pending_registrations'
    id = Column(Integer, primary_key=True)
    usn = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    face_encodings = Column(Text)  # JSON list base64
    status = Column(String(20), default='pending')  # pending/approved/rejected
    submitted_at = Column(TIMESTAMP, default=datetime.utcnow)

class ClassSetting(Base):
    __tablename__ = 'class_settings'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    slot_time = Column(String(50))  # e.g. '09:00-10:00'
    late_threshold = Column(Integer, default=5)  # minutes
    active = Column(Boolean, default=True)

class ClassSlot(Base):
    __tablename__ = 'class_slots'
    id = Column(Integer, primary_key=True)
    class_setting_id = Column(Integer, ForeignKey('class_settings.id'))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)

class SlotAttendance(Base):
    __tablename__ = 'slot_attendance'
    id = Column(Integer, primary_key=True)
    slot_id = Column(Integer, ForeignKey('class_slots.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(Enum(StatusEnum), default='absent')
    checkin_time = Column(Time)

# Engine/Session (SQLite default, MySQL via URL)
def get_engine(db_url='sqlite:///attendance.db'):
    return create_engine(db_url, echo=False)

def get_session():
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

# Create tables
def init_models(db_url='sqlite:///attendance.db'):
    engine = get_engine(db_url)
    Base.metadata.create_all(bind=engine)
    print('Models initialized')

if __name__ == '__main__':
    init_models()

