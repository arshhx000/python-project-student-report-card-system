from flask import Flask, render_template, request, redirect, url_for, flash, session
import database
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flash_messages'

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'teacher':
            flash('You do not have access to this page.', 'danger')
            return redirect(url_for('student_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ============ AUTH ROUTES ============

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        user = database.validate_user(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'teacher':
                flash('Welcome teacher!', 'success')
                return redirect(url_for('index'))
            else:  # student
                student = database.get_student_by_roll_no(username)
                if student:
                    session['student_id'] = student['id']
                    flash(f'Welcome {student["name"]}!', 'success')
                    return redirect(url_for('student_dashboard'))
                else:
                    flash('Student record not found.', 'danger')
                    session.clear()
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# ============ TEACHER ROUTES ============

@app.route('/')
@login_required
@teacher_required
def index():
    students = database.get_all_students()
    classes = set([s['class_name'] for s in students])
    
    # Calculate averages for each student
    for student in students:
        grades = database.get_grades_for_student(student['id'])
        student['average'] = database.get_student_average(student['id'])
    
    student_count = len(students)
    class_count = len(classes)
    avg_score = round(sum([s['average'] for s in students]) / len(students), 2) if students else 0
    
    return render_template('teacher_dashboard.html', students=students, student_count=student_count, 
                         class_count=class_count, avg_score=avg_score)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
@teacher_required
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        class_name = request.form['class_name']
        roll_no = request.form['roll_no']
        section = request.form.get('section', 'A')
        password = request.form.get('password', roll_no)  # Default password is roll number
        
        if name and class_name and roll_no:
            # Create user account for student
            user_id = database.create_user(roll_no, password, 'student')
            
            # Add student with user_id
            result = database.add_student(name, class_name, roll_no, section, user_id)
            
            if result:
                flash(f'Student {name} added successfully! (Password: {password})', 'success')
                return redirect(url_for('index'))
            else:
                flash('Roll number already exists.', 'danger')
        else:
            flash('Please fill out all required fields.', 'danger')
    
    return render_template('add_student.html')

@app.route('/manage_marks', methods=['GET', 'POST'])
@login_required
@teacher_required
def manage_marks():
    selected_student_id = request.args.get('student_id', type=int)
    selected_class = request.form.get('class') or request.args.get('class', '')
    
    if selected_class:
        students = database.get_students_by_class(selected_class)
    else:
        students = database.get_all_students()
    
    classes = sorted(set([s['class_name'] for s in students]))
    
    selected_student = None
    if selected_student_id:
        selected_student = database.get_student_by_id(selected_student_id)
        if selected_student:
            selected_student['grades'] = database.get_grades_for_student(selected_student_id)
    
    return render_template('manage_marks.html', students=students, classes=classes,
                         selected_student=selected_student, selected_student_id=selected_student_id,
                         selected_class=selected_class)

@app.route('/save_marks/<int:student_id>', methods=['POST'])
@login_required
@teacher_required
def save_marks(student_id):
    subject = request.form['subject']
    marks = request.form['marks']
    
    if subject and marks:
        try:
            marks = int(marks)
            if 0 <= marks <= 100:
                database.add_grade(student_id, subject, marks)
                flash(f'Marks for {subject} saved successfully!', 'success')
            else:
                flash('Marks must be between 0 and 100.', 'danger')
        except ValueError:
            flash('Marks must be a number.', 'danger')
    else:
        flash('Please fill out all fields.', 'danger')
    
    return redirect(url_for('manage_marks', student_id=student_id))

@app.route('/search_student', methods=['GET', 'POST'])
@login_required
@teacher_required
def search_student_page():
    query = request.args.get('query', '')
    results = []
    
    if query:
        results = database.search_student(query)
        for student in results:
            student['average'] = database.get_student_average(student['id'])
            grades = database.get_grades_for_student(student['id'])
            student['subject_count'] = len(grades)
            
            avg = student['average']
            if avg >= 90:
                student['grade'] = 'A+'
            elif avg >= 80:
                student['grade'] = 'A'
            elif avg >= 70:
                student['grade'] = 'B'
            elif avg >= 60:
                student['grade'] = 'C'
            elif avg >= 50:
                student['grade'] = 'D'
            else:
                student['grade'] = 'F'
    
    return render_template('search_student.html', results=results, query=query)

@app.route('/class_topper')
@login_required
@teacher_required
def class_topper():
    students = database.get_all_students()
    classes = sorted(set([s['class_name'] for s in students]))
    toppers = []
    
    for cls in classes:
        topper = database.get_class_topper(cls)
        if topper:
            toppers.append(topper)
    
    return render_template('class_topper.html', classes=classes, toppers=toppers)

@app.route('/fail_list')
@login_required
@teacher_required
def fail_list():
    students = database.get_all_students()
    classes = set([s['class_name'] for s in students])
    
    all_fail_records = []
    for cls in classes:
        fail_records = database.get_fail_list(cls)
        all_fail_records.extend(fail_records)
    
    # Add student id to fail records for linking
    for record in all_fail_records:
        record['id'] = record['student_id']
    
    return render_template('fail_list.html', fail_list=all_fail_records)

@app.route('/attendance', methods=['GET', 'POST'])
@login_required
@teacher_required
def attendance_page():
    selected_student_id = request.args.get('student_id', type=int)
    selected_class = request.form.get('class') or request.args.get('class', '')
    
    if selected_class:
        students = database.get_students_by_class(selected_class)
    else:
        students = database.get_all_students()
    
    classes = sorted(set([s['class_name'] for s in students]))
    
    selected_student = None
    student_attendance = []
    student_attendance_percent = 0
    
    if selected_student_id:
        selected_student = database.get_student_by_id(selected_student_id)
        if selected_student:
            student_attendance = database.get_attendance(selected_student_id)
            student_attendance_percent = database.get_attendance_percentage(selected_student_id)
    
    return render_template('attendance.html', students=students, classes=classes,
                         selected_student=selected_student, selected_student_id=selected_student_id,
                         student_attendance=student_attendance, student_attendance_percent=student_attendance_percent,
                         selected_class=selected_class)

@app.route('/save_attendance/<int:student_id>', methods=['POST'])
@login_required
@teacher_required
def save_attendance(student_id):
    date = request.form['date']
    status = request.form['status']
    
    if date and status:
        database.mark_attendance(student_id, date, status)
        flash('Attendance marked successfully!', 'success')
    else:
        flash('Please fill out all fields.', 'danger')
    
    return redirect(url_for('attendance_page', student_id=student_id))

@app.route('/remarks/<int:student_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def remarks_page(student_id):
    student = database.get_student_by_id(student_id)
    if not student:
        flash('Student not found!', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        remark = request.form['remark']
        if remark:
            database.add_remark(student_id, session['user_id'], remark)
            flash('Remark added successfully!', 'success')
    
    remarks = database.get_remarks(student_id)
    return render_template('remarks.html', student=student, remarks=remarks)

# ============ SHARED ROUTES ============

@app.route('/grades/<int:student_id>', methods=['GET', 'POST'])
@login_required
def manage_grades(student_id):
    student = database.get_student_by_id(student_id)
    if not student:
        flash('Student not found!', 'danger')
        return redirect(url_for('index' if session.get('role') == 'teacher' else 'student_dashboard'))

    if request.method == 'POST' and session.get('role') == 'teacher':
        subject = request.form['subject']
        marks = request.form['marks']
        if subject and marks:
            try:
                marks = int(marks)
                database.add_grade(student_id, subject, marks)
                flash('Grade added successfully!', 'success')
            except ValueError:
                flash('Marks must be a number.', 'danger')
        else:
            flash('Please fill out all fields.', 'danger')
            
    grades = database.get_grades_for_student(student_id)
    return render_template('grades.html', student=student, grades=grades)

@app.route('/delete_grade/<int:grade_id>', methods=['POST'])
@login_required
def delete_grade(grade_id):
    student_id = request.args.get('student_id', type=int)
    if session.get('role') == 'teacher':
        database.delete_grade(grade_id)
        flash('Grade deleted.', 'success')
        return redirect(url_for('manage_grades', student_id=student_id))
    flash('Unauthorized action.', 'danger')
    return redirect(url_for('student_dashboard'))

@app.route('/delete_grade/<int:student_id>/<int:grade_id>', methods=['POST'])
@login_required
@teacher_required
def delete_grade_alt(student_id, grade_id):
    database.delete_grade(grade_id)
    flash('Grade deleted.', 'success')
    return redirect(url_for('manage_grades', student_id=student_id))

@app.route('/report_card/<int:student_id>')
@login_required
def report_card(student_id):
    student = database.get_student_by_id(student_id)
    if not student:
        flash('Student not found!', 'danger')
        return redirect(url_for('index'))
        
    grades = database.get_grades_for_student(student_id)
    
    total_marks = sum([g['marks'] for g in grades]) if grades else 0
    num_subjects = len(grades)
    percentage = (total_marks / (num_subjects * 100)) * 100 if num_subjects > 0 else 0
    percentage = round(percentage, 2)
    
    grade_letter = 'F'
    if percentage >= 90:
        grade_letter = 'A+'
    elif percentage >= 80:
        grade_letter = 'A'
    elif percentage >= 70:
        grade_letter = 'B'
    elif percentage >= 60:
        grade_letter = 'C'
    elif percentage >= 50:
        grade_letter = 'D'
    
    # Get remarks
    remarks = database.get_remarks(student_id)
    
    return render_template('report_card.html', student=student, grades=grades, total_marks=total_marks, 
                         percentage=percentage, grade_letter=grade_letter, remarks=remarks)

@app.route('/delete_student/<int:student_id>', methods=['POST'])
@login_required
@teacher_required
def delete_student(student_id):
    database.delete_student(student_id)
    flash('Student deleted successfully.', 'success')
    return redirect(url_for('index'))

# ============ STUDENT ROUTES ============

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if session.get('role') != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    student_id = session.get('student_id')
    student = database.get_student_by_id(student_id)
    
    if not student:
        flash('Student record not found.', 'danger')
        return redirect(url_for('logout'))
    
    grades = database.get_grades_for_student(student_id)
    average = database.get_student_average(student_id)
    rank = database.get_class_rank(student_id)
    attendance_percentage = database.get_attendance_percentage(student_id)
    remarks = database.get_remarks(student_id)
    
    if average >= 90:
        grade_letter = 'A+'
    elif average >= 80:
        grade_letter = 'A'
    elif average >= 70:
        grade_letter = 'B'
    elif average >= 60:
        grade_letter = 'C'
    elif average >= 50:
        grade_letter = 'D'
    else:
        grade_letter = 'F'
    
    return render_template('student_dashboard.html', student=student, grades=grades, average=average,
                         rank=rank, attendance_percentage=attendance_percentage, grade_letter=grade_letter,
                         remarks=remarks)

if __name__ == '__main__':
    database.init_db()
    # Running on port 5001 to avoid conflicts
    app.run(debug=True, host='127.0.0.1', port=5001)


if __name__ == "__main__":
    app.run()

app = app
