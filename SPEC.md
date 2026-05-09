# Smart Attendance Tracker - Project Specification

## 1. Project Overview

**Project Name:** Smart Attendance Tracker
**Project Type:** Full-stack Web Application
**Core Functionality:** A comprehensive classroom management system with biometric attendance (face recognition), video lecture management, MCQ assessments, and AI chatbot support.
**Target Users:** Teachers and Students

---

## 2. Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Python (Flask)
- **Database:** MySQL
- **Face Recognition:** face_recognition library (Python)
- **Video Processing:** HTML5 Video API
- **AI Chatbot:** Simple rule-based chatbot with Python

---

## 3. UI/UX Specification

### Color Palette
- **Primary:** #1a1a2e (Deep Navy)
- **Secondary:** #16213e (Dark Blue)
- **Accent:** #e94560 (Coral Red)
- **Success:** #00d9a5 (Mint Green)
- **Warning:** #ffc107 (Amber)
- **Background:** #0f0f23 (Dark Background)
- **Card Background:** #1f1f3d (Purple-tinted Dark)
- **Text Primary:** #ffffff
- **Text Secondary:** #a0a0c0

### Typography
- **Primary Font:** 'Poppins', sans-serif
- **Headings:** Bold, 24px-36px
- **Body:** Regular, 14px-16px
- **Monospace:** 'Fira Code' for code/data

### Layout Structure
- **Responsive breakpoints:** 
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px

### Visual Effects
- Glassmorphism cards with backdrop blur
- Smooth transitions (0.3s ease)
- Animated gradient backgrounds
- Hover effects with scale and glow
- Custom scrollbars

---

## 4. Database Schema

### Tables

#### users
- id (INT, PRIMARY KEY)
- username (VARCHAR)
- password (VARCHAR)
- role (ENUM: 'student', 'teacher')
- name (VARCHAR)
- email (VARCHAR)
- created_at (TIMESTAMP)

#### subjects
- id (INT, PRIMARY KEY)
- name (VARCHAR)
- teacher_id (INT, FOREIGN KEY)
- created_at (TIMESTAMP)

#### attendance
- id (INT, PRIMARY KEY)
- student_id (INT, FOREIGN KEY)
- subject_id (INT, FOREIGN KEY)
- date (DATE)
- status (ENUM: 'present', 'absent', 'late')
- login_time (TIME)
- logout_time (TIME)
- face_verified (BOOLEAN)

#### videos
- id (INT, PRIMARY KEY)
- subject_id (INT, FOREIGN KEY)
- title (VARCHAR)
- description (TEXT)
- filename (VARCHAR)
- upload_date (TIMESTAMP)
- duration (INT)

#### video_views
- id (INT, PRIMARY KEY)
- video_id (INT, FOREIGN KEY)
- student_id (INT, FOREIGN KEY)
- watch_duration (INT)
- completed (BOOLEAN)
- view_date (TIMESTAMP)

#### mcq_tests
- id (INT, PRIMARY KEY)
- subject_id (INT, FOREIGN KEY)
- title (VARCHAR)
- topic (VARCHAR)
- created_by (INT)
- created_at (TIMESTAMP)

#### mcq_questions
- id (INT, PRIMARY KEY)
- test_id (INT, FOREIGN KEY)
- question (TEXT)
- option_a (VARCHAR)
- option_b (VARCHAR)
- option_c (VARCHAR)
- option_d (VARCHAR)
- correct_answer (CHAR)

#### test_results
- id (INT, PRIMARY KEY)
- test_id (INT, FOREIGN KEY)
- student_id (INT, FOREIGN KEY)
- score (INT)
- total_questions (INT)
- attempted_at (TIMESTAMP)

#### activity_log
- id (INT, PRIMARY KEY)
- student_id (INT, FOREIGN KEY)
- activity_type (VARCHAR)
- details (TEXT)
- timestamp (TIMESTAMP)

---

## 5. Feature Specifications

### 5.1 Authentication System
- Two separate login pages (student/teacher)
- Session management
- Password hashing
- Role-based access control

### 5.2 Face Recognition Attendance
- Webcam capture for face verification
- Compare with stored face encodings
- Mark attendance automatically
- Prevent fake attendance

### 5.3 Attendance Dashboard
- **Teacher View:**
  - Overall attendance percentage per subject
  - Individual student attendance
  - Date-wise attendance reports
  - Login/logout times
  
- **Student View:**
  - Personal attendance percentage per subject
  - Historical attendance records
  - Screen time tracking

### 5.4 Tab Switching & Inactivity Detection
- JavaScript event listeners for visibility change
- Track tab switches and warn user
- Log inactivity periods
- Teacher can view inactivity reports

### 5.5 Video Lecture Management
- **Teacher:**
  - Upload videos (MP4)
  - Add title, description, topic
  - View who watched each video
  - Track watch duration
  
- **Student:**
  - View available videos by subject
  - Watch videos
  - Progress tracking

### 5.6 MCQ Test System
- **Teacher:**
  - Create tests with questions
  - Set topic/subject
  - View all students' scores
  
- **Student:**
  - Take tests
  - View results immediately
  - View historical scores

### 5.7 AI Chatbot
- Rule-based FAQ system
- Help with navigation
- Answer common questions
- Available on all pages

---

## 6. Page Structure

### Pages to Create:
1. index.html - Landing page
2. login.html - Login selection
3. student_login.html - Student login
4. teacher_login.html - Teacher login
5. student_dashboard.html - Student dashboard
6. teacher_dashboard.html - Teacher dashboard
7. attendance.html - Attendance view
8. videos.html - Video library
9. video_player.html - Watch video
10. tests.html - MCQ tests
11. test_take.html - Take test
12. chatbot.html - AI chatbot widget

---

## 7. Acceptance Criteria

1. ✓ Two separate login systems for students and teachers
2. ✓ Face recognition based attendance marking
3. ✓ Attendance percentage visible for both roles
4. ✓ Screen time tracking with login/logout times
5. ✓ Tab switching prevention with warnings
6. ✓ Inactivity tracking in class
7. ✓ Video upload by teachers
8. ✓ Video viewing by students
9. ✓ Video attendance tracking
10. ✓ MCQ test creation and taking
11. ✓ Assessment scores visible to both
12. ✓ AI chatbot for help
13. ✓ Responsive design
14. ✓ Smooth animations and modern UI

