import sqlite3
import os

DB_PATH = 'attendance.db'

def migrate():
    if not os.path.exists(DB_PATH):
        print('Database not found. It will be created on next run.')
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add title column to live_classes if missing
    cursor.execute("PRAGMA table_info(live_classes)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'title' not in columns:
        cursor.execute("ALTER TABLE live_classes ADD COLUMN title VARCHAR(200)")
        print('Added title column to live_classes')
    else:
        print('title column already exists')

    # Create live_class_attendance table if missing
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='live_class_attendance'")
    if not cursor.fetchone():
        cursor.execute('''
            CREATE TABLE live_class_attendance (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                live_class_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                left_at TIMESTAMP,
                FOREIGN KEY(live_class_id) REFERENCES live_classes (id),
                FOREIGN KEY(student_id) REFERENCES users (id)
            )
        ''')
        print('Created live_class_attendance table')
    else:
        print('live_class_attendance table already exists')

    conn.commit()
    conn.close()
    print('Migration complete')

if __name__ == '__main__':
    migrate()

