import sqlite3
import hashlib

DB_FILE = 'database.db'

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create students table with roll number
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            section TEXT,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Create grades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT NOT NULL,
            marks INTEGER NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    ''')
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT NOT NULL,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    ''')
    
    # Create remarks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS remarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            teacher_id INTEGER,
            remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY(teacher_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Add default teacher account if not exists
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                      ('teacher', hash_password('admin123'), 'teacher'))
    except sqlite3.IntegrityError:
        pass  # Already exists
    
    conn.commit()
    conn.close()

def add_student(name, class_name, roll_no, section='A', user_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO students (name, class_name, roll_no, section, user_id) VALUES (?, ?, ?, ?, ?)', 
                      (name, class_name, roll_no, section, user_id))
        conn.commit()
        result = cursor.lastrowid
        conn.close()
        return result
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    conn.close()
    return students

def get_students_by_class(class_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE class_name = ? ORDER BY roll_no', (class_name,))
    students = cursor.fetchall()
    conn.close()
    return students

def get_student_by_id(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def get_student_by_roll_no(roll_no):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE roll_no = ?', (roll_no,))
    student = cursor.fetchone()
    conn.close()
    return student

def search_student(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE name LIKE ? OR roll_no LIKE ?', (f'%{query}%', f'%{query}%'))
    students = cursor.fetchall()
    conn.close()
    return students

def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
    cursor.execute('DELETE FROM grades WHERE student_id = ?', (student_id,))
    cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
    cursor.execute('DELETE FROM remarks WHERE student_id = ?', (student_id,))
    conn.commit()
    conn.close()

def add_grade(student_id, subject, marks):
    conn = get_connection()
    cursor = conn.cursor()
    # Update if exists, insert if not
    cursor.execute('SELECT id FROM grades WHERE student_id = ? AND subject = ?', (student_id, subject))
    existing = cursor.fetchone()
    if existing:
        cursor.execute('UPDATE grades SET marks = ? WHERE student_id = ? AND subject = ?', (marks, student_id, subject))
    else:
        cursor.execute('INSERT INTO grades (student_id, subject, marks) VALUES (?, ?, ?)', (student_id, subject, marks))
    conn.commit()
    conn.close()

def get_grades_for_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM grades WHERE student_id = ? ORDER BY subject', (student_id,))
    grades = cursor.fetchall()
    conn.close()
    return grades

def delete_grade(grade_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM grades WHERE id = ?', (grade_id,))
    conn.commit()
    conn.close()

# User authentication functions
def validate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                  (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                      (username, hash_password(password), role))
        conn.commit()
        result = cursor.lastrowid
        conn.close()
        return result
    except sqlite3.IntegrityError:
        conn.close()
        return None

# Attendance functions
def mark_attendance(student_id, date, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM attendance WHERE student_id = ? AND date = ?', (student_id, date))
    existing = cursor.fetchone()
    if existing:
        cursor.execute('UPDATE attendance SET status = ? WHERE student_id = ? AND date = ?', 
                      (status, student_id, date))
    else:
        cursor.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)', 
                      (student_id, date, status))
    conn.commit()
    conn.close()

def get_attendance(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM attendance WHERE student_id = ? ORDER BY date DESC', (student_id,))
    records = cursor.fetchall()
    conn.close()
    return records

def get_attendance_percentage(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total, SUM(CASE WHEN status = "P" THEN 1 ELSE 0 END) as present FROM attendance WHERE student_id = ?', 
                  (student_id,))
    result = cursor.fetchone()
    conn.close()
    if result['total'] > 0:
        return round((result['present'] / result['total']) * 100, 2)
    return 0

# Remarks functions
def add_remark(student_id, teacher_id, remark):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO remarks (student_id, teacher_id, remark) VALUES (?, ?, ?)', 
                  (student_id, teacher_id, remark))
    conn.commit()
    conn.close()

def get_remarks(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT r.*, u.username as teacher_name FROM remarks r 
                     LEFT JOIN users u ON r.teacher_id = u.id 
                     WHERE r.student_id = ? ORDER BY r.created_at DESC''', (student_id,))
    remarks = cursor.fetchall()
    conn.close()
    return remarks

# Analytics functions
def get_class_topper(class_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, AVG(g.marks) as average
        FROM students s
        LEFT JOIN grades g ON s.id = g.student_id
        WHERE s.class_name = ?
        GROUP BY s.id
        ORDER BY average DESC
        LIMIT 1
    ''', (class_name,))
    topper = cursor.fetchone()
    conn.close()
    return topper

def get_student_average(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(marks) as average FROM grades WHERE student_id = ?', (student_id,))
    result = cursor.fetchone()
    conn.close()
    return round(result['average'], 2) if result['average'] else 0

def get_class_rank(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Get student's class
    cursor.execute('SELECT class_name FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return None
    
    class_name = student['class_name']
    
    # Get student's average
    cursor.execute('SELECT AVG(marks) as avg FROM grades WHERE student_id = ?', (student_id,))
    student_avg = cursor.fetchone()['avg'] or 0
    
    # Count how many students have higher average
    cursor.execute('''
        SELECT COUNT(*) as count FROM (
            SELECT s.id, AVG(g.marks) as avg FROM students s
            LEFT JOIN grades g ON s.id = g.student_id
            WHERE s.class_name = ?
            GROUP BY s.id
            HAVING avg > ?
        ) as higher_students
    ''', (class_name, student_avg))
    
    rank = cursor.fetchone()['count'] + 1
    conn.close()
    return rank

def get_fail_list(class_name):
    """Get students who failed in any subject (marks < 50)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT s.id, s.name, s.roll_no, g.subject, g.marks
        FROM students s
        JOIN grades g ON s.id = g.student_id
        WHERE s.class_name = ? AND g.marks < 50
        ORDER BY s.roll_no, g.marks
    ''', (class_name,))
    fail_records = cursor.fetchall()
    conn.close()
    return fail_records
    conn.close()
