# 🎓 Student Report Card Management System

A comprehensive Flask-based web application for managing student records, grades, and report cards with role-based access control for teachers and students.

## 🌟 Features

### 🔐 Authentication & Authorization
- **Teacher Login**: Username & password authentication
- **Student Login**: Roll Number & password via student accounts
- **Role-Based Access Control**: Teachers have admin access, students have limited access
- **Session Management**: Secure session handling with automatic logout

### 👨‍🏫 Teacher Dashboard Features

#### 📊 Student Management
- ✅ Add new students with roll number and section
- ✅ View all students with their details and averages
- ✅ Search students by name or roll number
- ✅ Edit student information
- ✅ Delete student records (cascades to grades, attendance, remarks)

#### 📝 Marks Management
- ✅ Enter marks for students across multiple subjects
- ✅ Update existing marks
- ✅ Delete marks when needed
- ✅ Filter students by class
- ✅ Bulk mark entry from dashboard

#### 📋 Report Card Generation
- ✅ Generate official report cards with:
  - Subject-wise marks display
  - Total marks and percentage calculation
  - Automatic grade assignment (A+ to F)
  - Teacher remarks section
  - Print-friendly layout
- ✅ View, print, and export report cards

#### 📅 Attendance Tracking
- ✅ Mark attendance for students (Present/Absent/Leave)
- ✅ View attendance history
- ✅ Calculate attendance percentage
- ✅ Filter by class and track trends

#### 💬 Teacher Remarks
- ✅ Add remarks for individual students
- ✅ View all remarks with timestamps
- ✅ Display remarks on student report cards

#### 📊 Analytics & Reports
- ✅ **Class Topper**: View highest average scorer in each class
- ✅ **Fail List**: Students who scored below 50 in any subject
- ✅ **Class Statistics**: Student count, class count, average scores
- ✅ **Student Ranking**: Determine student rank in class based on average

### 👨‍🎓 Student Dashboard Features

#### 📚 View Academic Performance
- ✅ View own report card with all subjects
- ✅ See total marks and percentage
- ✅ Check letter grade (A+, A, B, C, D, F)
- ✅ View average score

#### 📊 Personal Statistics
- ✅ Class rank and comparison
- ✅ Attendance percentage
- ✅ Performance trend

#### 💬 View Teacher Remarks
- ✅ Read teacher feedback and remarks
- ✅ Track improvement suggestions

#### 🖨️ Print & Download
- ✅ Print personal report card
- ✅ Print-friendly formatting

## 📋 Grade System

The system automatically assigns grades based on percentage:

| Percentage Range | Grade | Performance |
|---|---|---|
| 90-100 | A+ | Outstanding |
| 80-89 | A | Excellent |
| 70-79 | B | Good |
| 60-69 | C | Average |
| 50-59 | D | Below Average |
| Below 50 | F | Fail |

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Flask 3.0.3
- SQLite3 (included with Python)

### Installation

1. **Clone/Download the project**
```bash
cd "e:\python project student report card system"
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Access the application**
Open your browser and go to: `http://127.0.0.1:5001`

## 🔑 Default Login Credentials

### Teacher Account
- **Username**: `teacher`
- **Password**: `admin123`

### Sample Student Account
Create students through the teacher dashboard. Each student gets:
- **Username**: Their Roll Number (e.g., `001`, `A001`)
- **Password**: Set during student creation (default: same as roll number)

## 📁 Project Structure

```
student-report-card-system/
├── app.py                      # Flask application with all routes
├── database.py                 # SQLite database functions
├── requirements.txt            # Python dependencies
├── database.db                 # SQLite database (auto-created)
└── templates/
    ├── base.html              # Base template with header/footer
    ├── login.html             # Login page (teacher & student)
    ├── index.html             # Teacher dashboard
    ├── student_dashboard.html  # Student dashboard
    ├── add_student.html       # Add student form
    ├── grades.html            # Grade management
    ├── manage_marks.html      # Bulk mark entry
    ├── report_card.html       # Report card template
    ├── search_student.html    # Search functionality
    ├── remarks.html           # Teacher remarks management
    ├── attendance.html        # Attendance tracking
    ├── class_topper.html      # Class topper analysis
    └── fail_list.html         # Fail list report
```

## 🗄️ Database Schema

### Tables
1. **users** - Login credentials (teacher & students)
2. **students** - Student information (name, roll no, class, section)
3. **grades** - Subject-wise marks
4. **attendance** - Daily attendance records
5. **remarks** - Teacher feedback and remarks

## 🔒 Security Features

- ✅ Password hashing using SHA-256
- ✅ Session-based authentication
- ✅ Role-based access control
- ✅ Input validation
- ✅ CSRF protection via Flash messages
- ✅ SQL injection prevention via parameterized queries

## 💡 Usage Guide

### For Teachers

1. **Login** with username `teacher` and password `admin123`
2. **Add Students** → Provide name, roll number, class, and section
3. **Enter Marks** → Select student and add subject-wise marks
4. **Generate Reports** → Create official report cards
5. **Track Analytics** → View class toppers and fail lists
6. **Manage Attendance** → Mark daily attendance
7. **Add Remarks** → Provide feedback to students

### For Students

1. **Login** with roll number and password provided by teacher
2. **View Dashboard** → See all personal academic information
3. **Check Grades** → View marks by subject and average
4. **See Rank** → Check standing in class
5. **Read Remarks** → View teacher feedback
6. **Print Report** → Download or print official report card

## 🔧 Configuration

Edit `app.py` to change:
- **Port**: Change `port=5001` to desired port
- **Debug Mode**: Change `debug=True` to `debug=False` for production
- **Secret Key**: Keep `app.secret_key` secure in production

## 📊 Advanced Features

### Analytics Available
- Class-wise total students
- Class-wise average scores
- Student performance rankings
- Pass/Fail statistics
- Attendance trends

### Customization Options
- Modify grade cutoffs in `app.py`
- Add more sections (A, B, C, D)
- Add more subjects across all students
- Extend attendance with leave types

## 🐛 Troubleshooting

### Issue: "Address already in use"
**Solution**: Change port in app.py or kill process on port 5001

### Issue: "No students found"
**Solution**: Login as teacher and add students first

### Issue: Database locked
**Solution**: Close other instances of the app, delete `database.db` and restart

## 📝 Future Enhancements

- [ ] PDF export using reportlab/fpdf2
- [ ] Email report cards to parents
- [ ] SMS notifications for results
- [ ] Bulk import from CSV
- [ ] Multiple semesters support
- [ ] Fee tracker module
- [ ] Timetable viewer
- [ ] Parent portal
- [ ] API for mobile app
- [ ] Dark mode theme

## 📜 LICENSE

This project is provided as-is for educational purposes.

## 🤝 Support

For issues or questions, review the code comments or add debugging by checking:
1. Browser console for frontend errors
2. Terminal output for backend errors
3. `database.db` for data consistency

---

**Version**: 2.0 (Enhanced with Authentication & Advanced Features)  
**Last Updated**: April 25, 2026
