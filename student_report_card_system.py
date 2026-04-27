import json
import os
from getpass import getpass
from datetime import datetime


SUBJECTS = ["Math", "Science", "English", "History", "Computer"]
DATA_FILE = "students.json"
HISTORY_FILE = "report_history.json"


class StudentReportCardSystem:
    def __init__(self):
        self.students = self._load_students()

    def _clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def _pause(self, msg="Press Enter to continue..."):
        input(msg)

    def _load_students(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def _save_students(self):
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(self.students, file, indent=4)

    def _log_report_history(self, student_id, generated_by):
        record = {
            "student_id": student_id,
            "generated_by": generated_by,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        history = []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                history = json.load(file)
                if not isinstance(history, list):
                    history = []
        except (FileNotFoundError, json.JSONDecodeError):
            history = []

        history.append(record)
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)

    def _generate_student_id(self):
        if not self.students:
            return "STU001"
        max_id = 0
        for student in self.students:
            sid = student.get("id", "")
            if sid.startswith("STU") and sid[3:].isdigit():
                max_id = max(max_id, int(sid[3:]))
        return f"STU{max_id + 1:03d}"

    def _validate_non_empty(self, field_name):
        while True:
            value = input(f"Enter {field_name}: ").strip()
            if value:
                return value
            print(f"{field_name} cannot be empty.")

    def _validate_marks(self, subject):
        while True:
            value = input(f"Enter marks for {subject} (0-100): ").strip()
            if not value.isdigit():
                print("Invalid input. Enter a number between 0 and 100.")
                continue
            marks = int(value)
            if 0 <= marks <= 100:
                return marks
            print("Marks must be between 0 and 100.")

    def _grade_from_marks(self, marks):
        if 90 <= marks <= 100:
            return "A+"
        if 80 <= marks <= 89:
            return "A"
        if 70 <= marks <= 79:
            return "B"
        if 60 <= marks <= 69:
            return "C"
        if 50 <= marks <= 59:
            return "D"
        return "F"

    def _calculate_summary(self, student):
        marks = student.get("subjects", {})
        total = sum(marks.get(subject, 0) for subject in SUBJECTS)
        percentage = total / len(SUBJECTS)
        subject_grades = {subject: self._grade_from_marks(marks.get(subject, 0)) for subject in SUBJECTS}
        result = "PASS" if all(marks.get(subject, 0) >= 50 for subject in SUBJECTS) else "FAIL"
        final_grade = self._grade_from_marks(round(percentage))
        return total, percentage, subject_grades, result, final_grade

    def _find_student_by_id(self, student_id):
        for student in self.students:
            if student.get("id") == student_id:
                return student
        return None

    def teacher_login(self):
        self._clear_screen()
        print("=== TEACHER LOGIN ===")
        username = input("Username: ").strip()
        password = getpass("Password: ").strip()
        return username == "teacher" and password == "teach123"

    def student_login(self):
        self._clear_screen()
        print("=== STUDENT LOGIN ===")
        student_id = input("Student ID: ").strip().upper()
        password = getpass("Password (name lowercase): ").strip()
        student = self._find_student_by_id(student_id)
        if not student:
            return None
        if student.get("name", "").lower() == password:
            return student
        return None

    def add_student(self):
        self._clear_screen()
        print("=== ADD STUDENT ===")
        name = self._validate_non_empty("Name")
        student_class = self._validate_non_empty("Class")
        section = self._validate_non_empty("Section").upper()
        student_id = self._generate_student_id()

        student = {
            "id": student_id,
            "name": name,
            "class": student_class,
            "section": section,
            "subjects": {subject: 0 for subject in SUBJECTS},
        }
        self.students.append(student)
        self._save_students()

        print(f"Student added successfully. Generated ID: {student_id}")
        print(f"Default password for student login: {name.lower()}")
        self._pause()

    def view_all_students(self):
        self._clear_screen()
        print("=== ALL STUDENTS ===")
        if not self.students:
            print("No student records found.")
            self._pause()
            return

        print(f"{'ID':<10}{'Name':<20}{'Class':<10}{'Section':<10}{'Percent':<10}{'Result':<8}")
        print("-" * 68)
        for student in self.students:
            total, percentage, _, result, _ = self._calculate_summary(student)
            _ = total
            print(
                f"{student['id']:<10}{student['name']:<20}{student['class']:<10}"
                f"{student['section']:<10}{percentage:>7.2f}%  {result:<8}"
            )
        self._pause()

    def search_student_by_name(self):
        self._clear_screen()
        print("=== SEARCH STUDENT BY NAME ===")
        query = input("Enter name to search: ").strip().lower()
        matches = [s for s in self.students if query in s.get("name", "").lower()]
        if not matches:
            print("No matching students found.")
            self._pause()
            return
        for student in matches:
            print(f"{student['id']} - {student['name']} (Class {student['class']}, Section {student['section']})")
        self._pause()

    def update_student_details(self):
        self._clear_screen()
        print("=== UPDATE STUDENT DETAILS ===")
        student_id = input("Enter Student ID: ").strip().upper()
        student = self._find_student_by_id(student_id)
        if not student:
            print("Student not found.")
            self._pause()
            return

        name = input(f"Name [{student['name']}]: ").strip()
        student_class = input(f"Class [{student['class']}]: ").strip()
        section = input(f"Section [{student['section']}]: ").strip().upper()

        if name:
            student["name"] = name
        if student_class:
            student["class"] = student_class
        if section:
            student["section"] = section

        self._save_students()
        print("Student details updated successfully.")
        self._pause()

    def enter_or_update_marks(self):
        self._clear_screen()
        print("=== ENTER/UPDATE MARKS ===")
        student_id = input("Enter Student ID: ").strip().upper()
        student = self._find_student_by_id(student_id)
        if not student:
            print("Student not found.")
            self._pause()
            return

        print(f"Entering marks for {student['name']} ({student['id']})")
        for subject in SUBJECTS:
            student["subjects"][subject] = self._validate_marks(subject)

        self._save_students()
        print("Marks updated successfully.")
        self._pause()

    def delete_student(self):
        self._clear_screen()
        print("=== DELETE STUDENT ===")
        student_id = input("Enter Student ID to delete: ").strip().upper()
        student = self._find_student_by_id(student_id)
        if not student:
            print("Student not found.")
            self._pause()
            return

        confirm = input(f"Are you sure you want to delete {student['name']}? (y/n): ").strip().lower()
        if confirm == "y":
            self.students = [s for s in self.students if s.get("id") != student_id]
            self._save_students()
            print("Student deleted successfully.")
        else:
            print("Delete cancelled.")
        self._pause()

    def _build_report_text(self, student):
        total, percentage, subject_grades, result, _ = self._calculate_summary(student)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "╔══════════════════════════════╗",
            "║     STUDENT REPORT CARD      ║",
            "╠══════════════════════════════╣",
            f"║ Name    : {student['name']:<18}║",
            f"║ ID      : {student['id']:<18}║",
            f"║ Class   : {student['class']} | Section: {student['section']:<6}║",
            "╠══════════════════════════════╣",
            "║ Subject     Marks   Grade    ║",
        ]

        for subject in SUBJECTS:
            marks = student["subjects"].get(subject, 0)
            grade = subject_grades.get(subject, "F")
            lines.append(f"║ {subject:<10} {marks:<7} {grade:<7}  ║")

        lines.extend(
            [
                "╠══════════════════════════════╣",
                f"║ Total  : {total:<3} / 500           ║",
                f"║ Percent: {percentage:<5.1f}%               ║",
                f"║ Result : {result:<18}║",
                "╚══════════════════════════════╝",
                f"Generated On: {now}",
            ]
        )
        return "\n".join(lines)

    def _export_report_txt(self, student, report_text):
        filename = f"report_{student['id']}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(report_text + "\n")
        return filename

    def generate_report_card(self):
        self._clear_screen()
        print("=== GENERATE REPORT CARD ===")
        print("1. Individual Student")
        print("2. All Students")
        choice = input("Choose option: ").strip()

        if choice == "1":
            student_id = input("Enter Student ID: ").strip().upper()
            student = self._find_student_by_id(student_id)
            if not student:
                print("Student not found.")
                self._pause()
                return
            report = self._build_report_text(student)
            print(report)
            self._log_report_history(student["id"], "teacher")
            export = input("Export to TXT? (y/n): ").strip().lower()
            if export == "y":
                filename = self._export_report_txt(student, report)
                print(f"Report exported: {filename}")
            self._pause()
            return

        if choice == "2":
            if not self.students:
                print("No student records found.")
                self._pause()
                return
            for student in self.students:
                report = self._build_report_text(student)
                print(report)
                print()
                self._log_report_history(student["id"], "teacher")
            self._pause()
            return

        print("Invalid option.")
        self._pause()

    def class_statistics(self):
        self._clear_screen()
        print("=== CLASS STATISTICS ===")
        if not self.students:
            print("No student records found.")
            self._pause()
            return

        percentages = []
        passed = 0
        subject_totals = {subject: 0 for subject in SUBJECTS}

        for student in self.students:
            _, percentage, _, result, _ = self._calculate_summary(student)
            percentages.append((student["id"], student["name"], percentage))
            if result == "PASS":
                passed += 1
            for subject in SUBJECTS:
                subject_totals[subject] += student["subjects"].get(subject, 0)

        class_avg = sum(p[2] for p in percentages) / len(percentages)
        topper = max(percentages, key=lambda x: x[2])
        pass_rate = (passed / len(self.students)) * 100

        print(f"Total Students   : {len(self.students)}")
        print(f"Class Average    : {class_avg:.2f}%")
        print(f"Pass Rate        : {pass_rate:.2f}%")
        print(f"Topper           : {topper[1]} ({topper[0]}) - {topper[2]:.2f}%")
        print("\nSubject Averages:")
        for subject in SUBJECTS:
            avg = subject_totals[subject] / len(self.students)
            print(f"- {subject:<10}: {avg:.2f}")

        print("\nLeaderboard (by percentage):")
        ranked = sorted(percentages, key=lambda x: x[2], reverse=True)
        for idx, row in enumerate(ranked, start=1):
            print(f"{idx}. {row[1]} ({row[0]}) - {row[2]:.2f}%")

        self._pause()

    def student_view_report(self, student):
        self._clear_screen()
        print("=== MY REPORT CARD ===")
        report = self._build_report_text(student)
        print(report)
        self._log_report_history(student["id"], "student")
        export = input("Export to TXT? (y/n): ").strip().lower()
        if export == "y":
            filename = self._export_report_txt(student, report)
            print(f"Report exported: {filename}")
        self._pause()

    def teacher_menu(self):
        while True:
            self._clear_screen()
            print("=== TEACHER MENU ===")
            print("1. Add Student")
            print("2. View All Students")
            print("3. Enter/Update Marks")
            print("4. Generate Report Card")
            print("5. Class Statistics")
            print("6. Delete Student")
            print("7. Update Student Details")
            print("8. Search Student by Name")
            print("9. Logout")
            choice = input("Enter choice: ").strip()

            if choice == "1":
                self.add_student()
            elif choice == "2":
                self.view_all_students()
            elif choice == "3":
                self.enter_or_update_marks()
            elif choice == "4":
                self.generate_report_card()
            elif choice == "5":
                self.class_statistics()
            elif choice == "6":
                self.delete_student()
            elif choice == "7":
                self.update_student_details()
            elif choice == "8":
                self.search_student_by_name()
            elif choice == "9":
                break
            else:
                print("Invalid choice.")
                self._pause()

    def student_menu(self, student):
        while True:
            self._clear_screen()
            print("=== STUDENT MENU ===")
            print("1. View My Report Card")
            print("2. Logout")
            choice = input("Enter choice: ").strip()

            if choice == "1":
                self.student_view_report(student)
            elif choice == "2":
                break
            else:
                print("Invalid choice.")
                self._pause()

    def run(self):
        while True:
            self._clear_screen()
            print("=== MAIN MENU ===")
            print("1. Teacher Login")
            print("2. Student Login")
            print("3. Exit")
            choice = input("Enter choice: ").strip()

            if choice == "1":
                if self.teacher_login():
                    self.teacher_menu()
                else:
                    print("Invalid teacher credentials.")
                    self._pause()
            elif choice == "2":
                student = self.student_login()
                if student:
                    self.student_menu(student)
                else:
                    print("Invalid student credentials.")
                    self._pause()
            elif choice == "3":
                print("Exiting...")
                break
            else:
                print("Invalid choice.")
                self._pause()


if __name__ == "__main__":
    app = StudentReportCardSystem()
    app.run()
