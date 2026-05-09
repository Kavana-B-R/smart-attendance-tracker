import pymongo
import datetime
import hashlib
from bson.binary import Binary
import pickle
import base64

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "smart_attendance"

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

print("🔗 Connected to MongoDB!")
print("📊 Creating collections & sample data...")

# Collections (auto-created on insert)
collections = [
    'users', 'subjects', 'videos', 'mcq_tests', 'mcq_questions', 
    'test_results', 'attendance', 'video_views', 'activity_log', 'screen_time'
]

for coll in collections:
    if coll not in db.list_collection_names():
        db.create_collection(coll)
        print(f"✅ Created: {coll}")
    else:
        print(f"📂 Exists: {coll}")

# Clear sample data (for clean setup)
db.users.delete_many({'username': {'$in': ['teacher1', 'student1']}})
db.subjects.delete_many({})

# Insert sample users
users = [
    {
        'username': 'teacher1',
        'password': hash_password('teacher123'),
        'role': 'teacher',
        'name': 'John Smith',
        'email': 'john.smith@school.com'
    },
    {
        'student_id': 'student1',
        'username': 'student1',
        'password': hash_password('student123'),
        'role': 'student',
        'name': 'Alice Johnson',
        'email': 'alice.johnson@school.com'
    }
]
result = db.users.insert_many(users)
print(f"👥 Inserted {len(users)} users. IDs: {result.inserted_ids}")

# Sample subjects
subjects = [
    {'name': 'Mathematics'},
    {'name': 'Physics'}
]
db.subjects.insert_many(subjects)
print("📚 Inserted subjects")

# Sample video
db.videos.insert_one({
    'title': 'Sample Lecture 1.mp4',
    'filename': 'sample1.mp4',
'upload_date': datetime.datetime.now()
})
print("🎥 Inserted sample video")

# Sample test
test_id = db.mcq_tests.insert_one({
    'title': 'Math Quiz 1',
    'subject_id': 0,  # First subject
    'topic': 'Algebra',
    'created_by': result.inserted_ids[0]
}).inserted_id

# Sample questions
questions = [
    {
        'test_id': test_id,
        'question': 'What is 2+2?',
        'option_a': '3', 'option_b': '4', 'option_c': '5', 'option_d': '6',
        'correct_answer': 'B'
    }
]
db.mcq_questions.insert_many(questions)
print("📝 Inserted sample test + question")

print("\n✅ Setup complete!")
print("\nLogin credentials:")
print("Teacher: teacher1 / teacher123")
print("Student: student1 / student123")
print("\n🔄 Run: python mongo_setup.py anytime to reset samples.")

client.close()

