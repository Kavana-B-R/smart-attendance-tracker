from models import init_models, get_engine, get_session, User, Subject, PendingRegistration
from app import hash_password

def create_sample_data():
    engine = get_engine()
    session = get_session()
    
    # Sample users
    password = hash_password('student123')
    student1 = User(student_id='student1', username='student1', password=password, role='student', name='Alice Johnson', email='alice@example.com')
    session.add(student1)
    
    password = hash_password('teacher123')
    teacher1 = User(username='teacher1', password=password, role='teacher', name='John Smith', email='john@example.com')
    session.add(teacher1)
    
    # Subjects
    math = Subject(name='Mathematics', teacher_id=teacher1.id)
    session.add(math)
    
    session.commit()
    print("Sample data created: student1/student123, teacher1/teacher123")
    
    # Sample pending
    pending = PendingRegistration(usn='newstudent', name='New Student', email='new@example.com', status='pending')
    session.add(pending)
    session.commit()
    print("Pending registration added for testing.")

if __name__ == '__main__':
    init_models()
    create_sample_data()

