from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_cors import CORS
import pymongo
from bson import ObjectId
import mysql.connector
import hashlib
import datetime
import os
import base64
import pickle
import numpy as np

app = Flask(__name__)
app.secret_key = 'smart_attendance_secret_key_2024'
CORS(app)

FACE_RECOGNITION_AVAILABLE = False
try:
    import cv2
    from face_recognition.api import face_encodings, compare_faces, face_locations
    FACE_RECOGNITION_AVAILABLE = True
    print("Face recognition available")
except ImportError:
    print("Face recognition not available - OpenCV fallback active")

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "smart_attendance"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_mongo_db():
    try:
        client = pymongo.MongoClient(MONGO_URI)
        return client[DB_NAME]
    except Exception as e:
        print(f"Mongo Error: {e}")
        return None

def get_db_connection():
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'hemanth kumar G',
        'database': 'smart_attendance'
    }
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"MySQL Error: {e}")
        return None

def get_user_by_credentials(identifier, password_hash, role):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM users WHERE 
        (username = %s OR student_id = %s) AND password = %s AND role = %s
    """, (identifier, identifier, password_hash, role))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def init_database():
    print("✅ MongoDB ready! (Collections created by mongo_setup.py)")

init_database()

UPLOAD_FOLDER = 'static/uploads/videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB for videos

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        password = hash_password(request.form['password'])
        user = get_user_by_credentials(student_id, password, 'student')
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = 'student'
            return redirect('/student/dashboard')
        return render_template('student_login.html', error='Invalid credentials')
    return render_template('student_login.html')

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        user = get_user_by_credentials(username, password, 'teacher')
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = 'teacher'
            return redirect('/teacher/dashboard')
        return render_template('teacher_login.html', error='Invalid credentials')
    return render_template('teacher_login.html')

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect('/teacher/login')
    
    db = get_mongo_db()
    if db is None:
        return "Database error", 500
    
    videos = list(db.videos.find().sort('upload_date', -1).limit(5))
    for v in videos:
        v['id'] = str(v['_id'])
        v.pop('_id')
    
    students = list(db.users.find({'role': 'student'}).limit(10))
    subjects = list(db.subjects.find())
    
    # Test results for dashboard
    test_results = []
    for result in db.test_results.find().sort('attempted_at', -1).limit(5):
        result['id'] = str(result['_id'])
        test_doc = db.mcq_tests.find_one({'_id': result['test_id']})
        result['title'] = test_doc['title'] if test_doc else 'Unknown Test'
        result['student_name'] = 'Student ' + str(result['student_id'])
        result['percentage'] = result['score'] / result['total_questions'] * 100
        test_results.append(result)
    
    data = {
        'videos': videos,
        'students': students,
        'subjects': subjects,
        'attendance_stats': [],
        'test_results': test_results,
        'recent_activity': []
    }
    
    return render_template('teacher_dashboard.html', data=data)

@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect('/student/login')
    
    db = get_mongo_db()
    if db is None:
        data = {'attendance': [], 'videos': [], 'test_results': [], 'screen_time': 0}
        return render_template('student_dashboard.html', data=data)
    
    # Attendance from MySQL
    conn = get_db_connection()
    attendance_data = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.name as subject_name, 
                   COUNT(DISTINCT a.id) as present,
                   COUNT(DISTINCT u.id) as total
            FROM attendance a
            JOIN users u ON a.student_id = u.id
            JOIN subjects s ON a.subject_id = s.id
            WHERE u.student_id = %s
            GROUP BY s.id
        """, (session['user_id'],))
        attendance_data = cursor.fetchall()
        cursor.close()
        conn.close()
    
    # Test results
    test_results = list(db.test_results.find({'student_id': int(session['user_id'])}).sort('attempted_at', -1).limit(5))
    for result in test_results:
        result['id'] = str(result['_id'])
        test_doc = db.mcq_tests.find_one({'_id': result['test_id']})
        result['title'] = test_doc['title'] if test_doc else 'Unknown Test'
        result['topic'] = test_doc.get('topic', 'General') if test_doc else 'General'
        result.pop('_id')
    
    videos = list(db.videos.find().limit(3))
    for v in videos:
        v.pop('_id', None)
        if 'upload_date' in v:
            if isinstance(v['upload_date'], datetime.datetime):
                v['upload_date'] = v['upload_date'].strftime('%Y-%m-%d')
            else:
                v['upload_date'] = str(v['upload_date'])[:10] if v['upload_date'] else 'Recent'
    
    data = {
        'attendance': attendance_data or [{'subject_name': 'Mathematics', 'present': 0, 'total': 0}],
        'videos': videos,
        'screen_time': 42,
        'test_results': test_results
    }
    return render_template('student_dashboard.html', data=data)

# ===== TEACHER TESTS ROUTES =====
@app.route('/teacher/tests')
@app.route('/teacher/tests/manage')
def teacher_tests():
    if session.get('role') != 'teacher':
        return redirect('/teacher/login')
    
    db = get_mongo_db()
    if db is None:
        return render_template('teacher_tests.html', tests=[])
    
    tests = list(db.mcq_tests.find().sort('created_at', -1))
    for test in tests:
        test['id'] = str(test['_id'])
        test['question_count'] = db.mcq_questions.count_documents({'test_id': test['_id']})
        test['attempts'] = db.test_results.count_documents({'test_id': test['_id']})
        results = list(db.test_results.find({'test_id': test['_id']}))
        test['avg_score'] = sum(r['score'] / r['total_questions'] for r in results) / len(results) if results else 0
        test.pop('_id')
    
    return render_template('teacher_tests.html', tests=tests)

@app.route('/teacher/tests/create', methods=['GET', 'POST'])
def teacher_test_create():
    if session.get('role') != 'teacher':
        return redirect('/teacher/login')
    
    db = get_mongo_db()
    if db is None:
        return "Database error", 500
    
    if request.method == 'POST':
        title = request.form['title']
        topic = request.form['topic']
        subject_id = int(request.form.get('subject_id', 0))
        
        test_doc = db.mcq_tests.insert_one({
            'title': title,
            'topic': topic,
            'subject_id': subject_id,
            'created_by': int(session['user_id']),
            'created_at': datetime.datetime.now()
        })
        
        test_id = str(test_doc.inserted_id)
        # Add questions
        for i in range(1, 11):  # Max 10
            question_key = f'question_{i}'
            if question_key in request.form and request.form[question_key].strip():
                db.mcq_questions.insert_one({
                    'test_id': ObjectId(test_id),
                    'question': request.form[question_key],
                    'option_a': request.form[f'option_a_{i}'],
                    'option_b': request.form[f'option_b_{i}'],
                    'option_c': request.form[f'option_c_{i}'],
                    'option_d': request.form[f'option_d_{i}'],
                    'correct_answer': request.form[f'correct_{i}'].upper()
                })
        
        return redirect(f'/teacher/tests/{test_id}/detail')
    
    subjects = list(db.subjects.find())
    return render_template('teacher_test_manage.html', test=None, questions=[], subjects=subjects)

@app.route('/teacher/tests/<test_id>/detail')
def teacher_test_detail(test_id):
    if session.get('role') != 'teacher':
        return redirect('/teacher/login')
    
    db = get_mongo_db()
    if db is None:
        return "Database error", 500
    
    test = db.mcq_tests.find_one({'_id': ObjectId(test_id)})
    if not test:
        return "Test not found", 404
    
    test['id'] = str(test['_id'])
    test.pop('_id')
    test['question_count'] = db.mcq_questions.count_documents({'test_id': ObjectId(test_id)})
    
    results = list(db.test_results.find({'test_id': ObjectId(test_id)}).sort('attempted_at', -1))
    for result in results:
        result['student_name'] = 'Student ' + str(result['student_id'])
        result['percentage'] = (result['score'] / result['total_questions']) * 100 if result['total_questions'] > 0 else 0
        result['date'] = result['attempted_at'].strftime('%Y-%m-%d %H:%M') if result['attempted_at'] else 'N/A'
    
    attempts = len(results)
    avg_score = sum(r['percentage'] for r in results) / attempts if attempts > 0 else 0
    top_score = max([r['percentage'] for r in results], default=0)
    pass_rate = len([r for r in results if r['percentage'] >= 60]) / attempts * 100 if attempts > 0 else 0
    
    return render_template('teacher_test_detail.html', test=test, results=results, attempts=attempts, avg_score=avg_score, top_score=top_score, pass_rate=pass_rate)

# Other existing routes...
@app.route('/student/attendance')
def student_attendance():
    if session.get('role') != 'student':
        return redirect('/student/login')
    
    db = get_mongo_db()
    if db is None:
        return render_template('student_attendance.html', subjects=[], recent_attendance=[])
    
    subjects = list(db.subjects.find({}, {'name': 1, '_id': 0}))
    
    user_id = int(session['user_id'])
    recent_attendance = list(db.attendance.find({'student_id': user_id}).sort('date', -1).limit(20))
    subjects_dict = {str(s['_id']): s['name'] for s in db.subjects.find()}
    
    for att in recent_attendance:
        att['date_str'] = att['date'].strftime('%Y-%m-%d') if hasattr(att['date'], 'strftime') else str(att['date'])[:10]
        att['time_str'] = att.get('time', 'N/A')
        att['status_class'] = 'status-present' if att['status'] == 'present' else 'status-absent'
        att['subject_name'] = subjects_dict.get(str(att.get('subject_id')), 'Unknown')
    
    return render_template('student_attendance.html', subjects=subjects, recent_attendance=recent_attendance)

@app.route('/register_face', methods=['POST'])
def register_face():
    data = request.json
    descriptor = np.array(data['descriptor'], dtype='float32')
    
    student_id = session.get('username', 'student1')
    
    enc_bytes = pickle.dumps(descriptor)
    enc_b64 = base64.b64encode(enc_bytes).decode()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET face_encoding = %s WHERE student_id = %s", (enc_b64, student_id))
    updated = cursor.rowcount > 0
    
    conn.commit()
    cursor.close()
    conn.close()
    
    if updated:
        return jsonify({'success': True, 'message': f'Face saved for {student_id}!'})
    else:
        return jsonify({'success': False, 'message': f'No student {student_id} found'})

@app.route('/face_register')
def face_register():
    return render_template('face_register.html')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    face_data = data['face_data']
    subject_id = 1
    
    try:
        img_data = base64.b64decode(face_data)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({'success': False, 'message': 'Invalid image'})
    except:
        return jsonify({'success': False, 'message': 'Decode error'})
    
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return jsonify({'success': False, 'message': 'No face detected'})

    (x,y,w,h) = faces[0]
    face_roi = gray[y:y+h, x:x+w]
    embedding = cv2.resize(face_roi, (32,32)).flatten().astype(np.float32)/255.0
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT face_encoding FROM users WHERE student_id = %s", (session['username'],))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not student or not student['face_encoding']:
        return jsonify({'success': False, 'message': 'Register your face first!'})
    
    reg_vec = pickle.loads(base64.b64decode(student['face_encoding']))
    distance = np.linalg.norm(embedding - reg_vec)
    
    if distance < 0.25:
        db = get_mongo_db()
        if db:
            user_id = int(session['user_id'])
            db.attendance.insert_one({
                'student_id': user_id,
                'subject_id': int(subject_id),
                'status': 'present',
                'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'distance': round(distance, 3),
                'face_verified': True
            })
        return jsonify({'success': True, 'message': f'Attendance marked! Confidence: {1-distance:.1%}'})
    else:
        return jsonify({'success': False, 'message': f'Face mismatch ({distance:.3f}). Try again.'})

@app.route('/student/tests')
def student_tests():
    if session.get('role') != 'student':
        return redirect('/student/login')
    
    db = get_mongo_db()
    tests = []
    if db:
        tests = list(db.mcq_tests.find().sort('created_at', -1).limit(10))
        subjects_dict = dict([(str(s['_id']), s['name']) for s in db.subjects.find({}, {'name': 1})])
    
        for test in tests:
            test['id'] = str(test['_id'])
            test['subject_name'] = subjects_dict.get(str(test.get('subject_id')), 'Unknown')
            test.pop('_id')
    
    return render_template('tests.html', tests=tests)

@app.route('/test/<test_id>')
def take_test(test_id):
    if session.get('role') != 'student':
        return redirect('/student/login')
    
    db = get_mongo_db()
    test = None
    questions = []
    if db:
        test_doc = db.mcq_tests.find_one({'_id': ObjectId(test_id)})
        questions = list(db.mcq_questions.find({'test_id': ObjectId(test_id)}))
        if test_doc:
            test = {
                'id': str(test_doc['_id']),
                'title': test_doc['title'],
                'topic': test_doc.get('topic', 'General')
            }
            for q in questions:
                q['id'] = str(q['_id'])
                q.pop('_id')
    
    if not test:
        return "Test not found", 404
    
    return render_template('test_take.html', test=test, questions=questions)

@app.route('/test/submit/<test_id>', methods=['POST'])
def submit_test(test_id):
    data = request.json['answers']
    
    db = get_mongo_db()
    if not db:
        return jsonify({'success': False})
    
    questions = list(db.mcq_questions.find({'test_id': ObjectId(test_id)}))
    correct_answers = {str(q['_id']): q['correct_answer'] for q in questions}
    
    score = 0
    total = len(correct_answers)
    for qid, user_answer in data.items():
        if qid in correct_answers and user_answer == correct_answers[qid]:
            score += 1
    
    user_id = int(session['user_id'])
    db.test_results.insert_one({
        'test_id': ObjectId(test_id),
        'student_id': user_id,
        'score': score,
        'total_questions': total,
        'attempted_at': datetime.datetime.now()
    })
    
    return jsonify({'success': True, 'score': score, 'total': total})

@app.route('/teacher/videos/manage', methods=['GET', 'POST', 'DELETE'])
def teacher_videos_manage():
    if session.get('role') != 'teacher':
        return redirect('/teacher/login')
    
    db = get_mongo_db()
    if request.method == 'DELETE':
        video_id = request.json.get('id')
        if db and video_id:
            video = db.videos.find_one({'_id': ObjectId(video_id)})
            if video:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], video['filename'])
                if os.path.exists(file_path):
                    os.remove(file_path)
                db.videos.delete_one({'_id': ObjectId(video_id)})
                return jsonify({'success': True, 'message': 'Video deleted!'})
        return jsonify({'success': False, 'message': 'Video not found'})
    
    if request.method == 'POST':
        if 'video' not in request.files:
            return jsonify({'success': False, 'message': 'No file'})
        file = request.files['video']
        title = request.form.get('title', 'Untitled')
        if file.filename:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            result = db.videos.insert_one({
                'title': title,
                'filename': filename,
                'upload_date': datetime.datetime.now()
            })
            return jsonify({'success': True, 'message': f'Video uploaded! ID: {result.inserted_id}'})
        return jsonify({'success': False, 'message': 'Upload failed'})
    
    # GET list
    videos = list(db.videos.find().sort('upload_date', -1))
    for v in videos:
        v['id'] = str(v['_id'])
        v.pop('_id')
        if 'upload_date' in v:
            try:
                if hasattr(v['upload_date'], 'strftime'):
                    v['upload_date'] = v['upload_date'].strftime('%Y-%m-%d %H:%M')
                else:
                    v['upload_date'] = str(v['upload_date'])[:16] if v['upload_date'] else 'Recent'
            except:
                v['upload_date'] = 'Recent'
    return render_template('manage_videos.html', videos=videos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/static/uploads/videos/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/activity/log', methods=['POST'])
def activity_log():
    data = request.json
    db = get_mongo_db()
    if db is not None:
        db.activity_log.insert_one({
            'student_id': int(session.get('user_id', 0)),
            'activity_type': data.get('type', 'unknown'),
            'details': data.get('details', ''),
            'timestamp': datetime.datetime.now()
        })
    return jsonify({'success': True})


@app.route('/api/inactivity', methods=['POST'])
def inactivity_log():
    data = request.json
    db = get_mongo_db()
    if db is not None:
        db.activity_log.insert_one({
            'student_id': int(session.get('user_id', 0)),
            'activity_type': 'inactivity',
            'details': data.get('duration', 0),
            'timestamp': datetime.datetime.now()
        })
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)

