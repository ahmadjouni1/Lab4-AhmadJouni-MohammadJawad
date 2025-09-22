from __future__ import annotations
from typing import List
import re, csv
from PyQt5 import QtWidgets, QtCore
from data.db_sqlite import SchoolDBSqlite
from models.student import Student
from models.instructor import Instructor
from models.course import Course


EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def validate_email(s: str):
    """Validate email format using a regular expression.
    :param s: Email string to validate
    :type s: str
    :raises ValueError: if email format is invalid
    :return: None
    """
    if not EMAIL_RE.match(s or ""):
        raise ValueError("Invalid email format.")

def validate_nonneg_int(s: str, field_name: str = "Age") -> int:
    """Validate that the input string represents a non-negative integer.
    :param s: String to validate
    :type s: str
    :param field_name: Name of the field for error messages"""
    try:
        v = int(s)
    except Exception:
        raise ValueError(f"{field_name} must be an integer.")
    if v < 0:
        raise ValueError(f"{field_name} must be non-negative.")
    return v


class SchoolWindow(QtWidgets.QMainWindow):
    """Main window for the School Management System GUI using PyQt5
    :param db: Instance of SchoolDBSqlite for database operations
    :type db: SchoolDBSqlite
    """
    def __init__(self, db: SchoolDBSqlite):
        super().__init__()
        self.db = db
        self.setWindowTitle("School Management System")
        self.resize(1000, 640)

        
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        vroot = QtWidgets.QVBoxLayout(central)

        
        self.tabs = QtWidgets.QTabWidget()
        vroot.addWidget(self.tabs)

        self.tab_add = QtWidgets.QWidget()
        self.tab_reg = QtWidgets.QWidget()
        self.tab_view = QtWidgets.QWidget()

        self.tabs.addTab(self.tab_add, "Add Records")
        self.tabs.addTab(self.tab_reg, "Registration & Assignment")
        self.tabs.addTab(self.tab_view, "View / Search")

        self._build_add_tab()
        self._build_reg_tab()
        self._build_view_tab()

        self._build_menu()
        self.refresh_all()

   
    def _build_menu(self):
        """Create the menu bar with file operations.
        :return: None"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        act_open   = QtWidgets.QAction("Open Database…", self)
        act_backup = QtWidgets.QAction("Backup Database…", self)
        act_load   = QtWidgets.QAction("Load JSON…", self)
        act_save   = QtWidgets.QAction("Save JSON…", self)
        act_export = QtWidgets.QAction("Export CSV…", self)
        act_exit   = QtWidgets.QAction("Exit", self)

        act_open.triggered.connect(self.on_open_db)
        act_backup.triggered.connect(self.on_backup_db)
        act_load.triggered.connect(self.on_load)
        act_save.triggered.connect(self.on_save)
        act_export.triggered.connect(self.on_export_csv)
        act_exit.triggered.connect(self.close)

        file_menu.addAction(act_open)
        file_menu.addAction(act_backup)
        file_menu.addSeparator()
        file_menu.addAction(act_load)
        file_menu.addAction(act_save)
        file_menu.addAction(act_export)
        file_menu.addSeparator()
        file_menu.addAction(act_exit)

    def on_open_db(self):
        """Open or create a new SQLite database file.
        :return: None
        :param path: Path to the database file"""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Open/Create Database", "", "SQLite DB (*.db)")
        if not path:
            return
        try:
            self.db.close()
        except Exception:
            pass
        self.db = SchoolDBSqlite(path)
        self.refresh_all()
        QtWidgets.QMessageBox.information(self, "Database", f"Connected to:\n{path}")

    def on_backup_db(self):
        """Backup the current database to a specified file.
        :return: None
        :param path: Path to save the backup database file
        """
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Backup Database", "", "SQLite DB (*.db)")
        if not path:
            return
        try:
            self.db.backup_db(path)
            QtWidgets.QMessageBox.information(self, "Backup", f"Database copied to:\n{path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def on_load(self):
        """Load data from a JSON file into the database.
        :return: None"""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load JSON", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            self.db = SchoolDBSqlite.load_json(path, getattr(self.db, "db_path", "school.db"))
            self.refresh_all()
            QtWidgets.QMessageBox.information(self, "Loaded", f"Loaded JSON into DB:\n{self.db.db_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def on_save(self):
        """Save the current database state to a JSON file.
        :return: None
        """
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            self.db.save_json(path)
            QtWidgets.QMessageBox.information(self, "Saved", f"Saved JSON:\n{path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def on_export_csv(self):
        """Export all records to a CSV file.
        :return: None"""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            rows = []
            
            for s in self.db.students.values():
                extra = ", ".join(c.course_id for c in s.registered_courses) or "-"
                rows.append(("Student", s.student_id, s.name, extra))
            
            for i in self.db.instructors.values():
                extra = ", ".join(c.course_id for c in i.assigned_courses) or "-"
                rows.append(("Instructor", i.instructor_id, i.name, extra))
            
            for c in self.db.courses.values():
                extra = f"Instr: {c.instructor.name if c.instructor else '—'}, Enrolled: {len(c.enrolled_students)}"
                rows.append(("Course", c.course_id, c.course_name, extra))

            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Type", "ID", "Name", "Extra"])
                w.writerows(rows)

            QtWidgets.QMessageBox.information(self, "Exported", f"CSV saved to: {path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    
    def _build_add_tab(self):
        """Create the 'Add Records' tab with forms to add students, instructors, and courses.
        :return: None"""
        grid = QtWidgets.QGridLayout(self.tab_add)

        
        gs = QtWidgets.QGroupBox("Add Student")
        s_layout = QtWidgets.QFormLayout(gs)
        self.s_name = QtWidgets.QLineEdit()
        self.s_age = QtWidgets.QLineEdit()
        self.s_email = QtWidgets.QLineEdit()
        self.s_id = QtWidgets.QLineEdit()
        s_btn = QtWidgets.QPushButton("Add Student")
        s_btn.clicked.connect(self.add_student)
        s_layout.addRow("Name", self.s_name)
        s_layout.addRow("Age", self.s_age)
        s_layout.addRow("Email", self.s_email)
        s_layout.addRow("Student ID", self.s_id)
        s_layout.addRow(s_btn)

       
        gi = QtWidgets.QGroupBox("Add Instructor")
        i_layout = QtWidgets.QFormLayout(gi)
        self.i_name = QtWidgets.QLineEdit()
        self.i_age = QtWidgets.QLineEdit()
        self.i_email = QtWidgets.QLineEdit()
        self.i_id = QtWidgets.QLineEdit()
        i_btn = QtWidgets.QPushButton("Add Instructor")
        i_btn.clicked.connect(self.add_instructor)
        i_layout.addRow("Name", self.i_name)
        i_layout.addRow("Age", self.i_age)
        i_layout.addRow("Email", self.i_email)
        i_layout.addRow("Instructor ID", self.i_id)
        i_layout.addRow(i_btn)

        
        gc = QtWidgets.QGroupBox("Add Course")
        c_layout = QtWidgets.QFormLayout(gc)
        self.c_id = QtWidgets.QLineEdit()
        self.c_name = QtWidgets.QLineEdit()
        self.c_instr = QtWidgets.QComboBox()
        c_btn = QtWidgets.QPushButton("Add Course")
        c_btn.clicked.connect(self.add_course)
        c_layout.addRow("Course ID", self.c_id)
        c_layout.addRow("Course Name", self.c_name)
        c_layout.addRow("Instructor", self.c_instr)
        c_layout.addRow(c_btn)

        grid.addWidget(gs, 0, 0)
        grid.addWidget(gi, 0, 1)
        grid.addWidget(gc, 1, 0, 1, 2)

    def add_student(self):
        """Add a new student to the database.

    Validates input fields (name, age, email, ID). Shows a success or
    error message depending on the outcome.

    Raises:
        ValueError: If age is negative/non-integer or the email format is invalid.

    Returns:
        None
    """
        try:
            name = self.s_name.text().strip()
            age = validate_nonneg_int(self.s_age.text().strip(), "Age")
            email = self.s_email.text().strip()
            validate_email(email)
            sid = self.s_id.text().strip()
            s = Student(name, age, email, sid)
            self.db.add_student(s)
            self.s_name.clear(); self.s_age.clear(); self.s_email.clear(); self.s_id.clear()
            QtWidgets.QMessageBox.information(self, "OK", "Student added.")
            self.refresh_all()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def add_instructor(self):
        """Add a new instructor to the database.

    Validates input fields (name, age, email, instructor ID). Shows a success or
    error message depending on the outcome.

    Raises:
        ValueError: If age is negative/non-integer or the email format is invalid.

    Returns:
        None
    """
        try:
            name = self.i_name.text().strip()
            age = validate_nonneg_int(self.i_age.text().strip(), "Age")
            email = self.i_email.text().strip()
            validate_email(email)
            iid = self.i_id.text().strip()
            ins = Instructor(name, age, email, iid)
            self.db.add_instructor(ins)
            self.i_name.clear(); self.i_age.clear(); self.i_email.clear(); self.i_id.clear()
            QtWidgets.QMessageBox.information(self, "OK", "Instructor added.")
            self.refresh_all()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def add_course(self):
        """
         Add a new course to the database.

    Optionally associates an instructor selected from the combo box.
    Shows a success or error message depending on the outcome.

    Raises:
        ValueError: If course ID or course name is empty.

    Returns:
        None
         """
        try:
            instr_text = self.c_instr.currentText()
            instr_id = instr_text.split(" | ")[0] if instr_text else None
            instr = self.db.instructors.get(instr_id) if instr_id else None
            c = Course(self.c_id.text().strip(), self.c_name.text().strip(), instr)
            self.db.add_course(c)
            self.c_id.clear(); self.c_name.clear(); self.c_instr.setCurrentIndex(-1)
            QtWidgets.QMessageBox.information(self, "OK", "Course added.")
            self.refresh_all()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

   
    def _build_reg_tab(self):
        """Create the 'Registration & Assignment' tab with forms to register students to courses and assign instructors to courses.

        """
        v = QtWidgets.QVBoxLayout(self.tab_reg)

        
        gr = QtWidgets.QGroupBox("Student Registration")
        fr = QtWidgets.QGridLayout(gr)
        self.reg_student = QtWidgets.QComboBox()
        self.reg_course = QtWidgets.QComboBox()
        breg = QtWidgets.QPushButton("Register")
        breg.clicked.connect(self.register_student)
        fr.addWidget(QtWidgets.QLabel("Student"), 0, 0)
        fr.addWidget(self.reg_student, 0, 1)
        fr.addWidget(QtWidgets.QLabel("Course"), 1, 0)
        fr.addWidget(self.reg_course, 1, 1)
        fr.addWidget(breg, 0, 2, 2, 1)
        v.addWidget(gr)

       
        ga = QtWidgets.QGroupBox("Instructor Assignment")
        fa = QtWidgets.QGridLayout(ga)
        self.ass_course = QtWidgets.QComboBox()
        self.ass_instr = QtWidgets.QComboBox()
        bass = QtWidgets.QPushButton("Assign")
        bass.clicked.connect(self.assign_instructor)
        fa.addWidget(QtWidgets.QLabel("Course"), 0, 0)
        fa.addWidget(self.ass_course, 0, 1)
        fa.addWidget(QtWidgets.QLabel("Instructor"), 1, 0)
        fa.addWidget(self.ass_instr, 1, 1)
        fa.addWidget(bass, 0, 2, 2, 1)
        v.addWidget(ga)
        v.addStretch(1)

    def register_student(self):
        """
        register the selected students into the selected course.
        :returns: None
        """
        try:
            sid = self.reg_student.currentText().split(" | ")[0]
            cid = self.reg_course.currentText().split(" | ")[0]
            self.db.register_student_in_course(sid, cid)
            QtWidgets.QMessageBox.information(self, "OK", "Student registered to course.")
            self.refresh_all()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def assign_instructor(self):
        """
        assign the selected instructor to the selected course.
        :returns: None
        """
        try:
            cid = self.ass_course.currentText().split(" | ")[0]
            iid = self.ass_instr.currentText().split(" | ")[0]
            self.db.assign_instructor_to_course(iid, cid)
            QtWidgets.QMessageBox.information(self, "OK", "Instructor assigned to course.")
            self.refresh_all()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

   
    def _build_view_tab(self):
        """
        Create the 'View' tab with a table to display all entities (students, instructors, courses).
        :returns: None
        """
        v = QtWidgets.QVBoxLayout(self.tab_view)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(QtWidgets.QLabel("Search"))
        self.search_edit = QtWidgets.QLineEdit()
        top.addWidget(self.search_edit)
        go = QtWidgets.QPushButton("Go")
        clr = QtWidgets.QPushButton("Clear")
        go.clicked.connect(self.on_search)
        clr.clicked.connect(self.on_clear)
        top.addWidget(go); top.addWidget(clr)
        v.addLayout(top)

        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Type", "ID", "Name", "Extra"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        v.addWidget(self.table, 1)

        
        btns = QtWidgets.QHBoxLayout()
        self.btn_edit = QtWidgets.QPushButton("Edit Selected")
        self.btn_del  = QtWidgets.QPushButton("Delete Selected")
        self.btn_csv  = QtWidgets.QPushButton("Export CSV")
        self.btn_edit.clicked.connect(self.edit_selected)
        self.btn_del.clicked.connect(self.delete_selected)
        self.btn_csv.clicked.connect(self.on_export_csv)
        btns.addWidget(self.btn_edit); btns.addWidget(self.btn_del); btns.addWidget(self.btn_csv)
        v.addLayout(btns)

    def on_search(self):
        """Perform a search based on the input text and update the table with results.
         :return: None"""
        q = self.search_edit.text().strip()
        res = self.db.search(q)
        self._fill_table(res)

    def on_clear(self):
        """Clear the search input and refresh the table to show all records.
        :return: None"""
        self.search_edit.clear()
        self.refresh_table()

   
    def refresh_all(self):
        """Refresh all UI components to reflect the current state of the database.
            :return: None"""
        self.db.refresh_cache()
       
        self.c_instr.clear()
        self.c_instr.addItems([f"{i.instructor_id} | {i.name}" for i in self.db.instructors.values()])
        self.c_instr.setCurrentIndex(-1)

        self.reg_student.clear()
        self.reg_student.addItems([f"{s.student_id} | {s.name}" for s in self.db.students.values()])
        self.reg_student.setCurrentIndex(-1)

        self.reg_course.clear()
        self.reg_course.addItems([f"{c.course_id} | {c.course_name}" for c in self.db.courses.values()])
        self.reg_course.setCurrentIndex(-1)

        self.ass_course.clear()
        self.ass_course.addItems([f"{c.course_id} | {c.course_name}" for c in self.db.courses.values()])
        self.ass_course.setCurrentIndex(-1)

        self.ass_instr.clear()
        self.ass_instr.addItems([f"{i.instructor_id} | {i.name}" for i in self.db.instructors.values()])
        self.ass_instr.setCurrentIndex(-1)

        self.refresh_table()

    def refresh_table(self):
        """Refresh the table to show the current state of the database.
        :return: None
        """
        res = {
            "students": list(self.db.students.values()),
            "instructors": list(self.db.instructors.values()),
            "courses": list(self.db.courses.values()),
        }
        self._fill_table(res)

    def _fill_table(self, res):
        """Fill the table with data from the database.
        :param res: The result set containing students, instructors, and courses.
        :return: None
        """
        rows: List[tuple] = []

        for s in res["students"]:
            extra = ", ".join(c.course_id for c in s.registered_courses) or "-"
            rows.append(("Student", s.student_id, s.name, extra))

        for i in res["instructors"]:
            extra = ", ".join(c.course_id for c in i.assigned_courses) or "-"
            rows.append(("Instructor", i.instructor_id, i.name, extra))

        for c in res["courses"]:
            extra = f"Instr: {c.instructor.name if c.instructor else '—'}, Enrolled: {len(c.enrolled_students)}"
            rows.append(("Course", c.course_id, c.course_name, extra))

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for col, val in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(val))
                # make table read-only
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                self.table.setItem(r, col, item)

   
    def _get_selected_record(self):
        """Get the type and ID of the currently selected record in the table.
        :return: Tuple of (record type, record ID) or (None, None) if no selection"""
        row = self.table.currentRow()
        if row < 0:
            return None, None
        r_type = self.table.item(row, 0).text()
        r_id   = self.table.item(row, 1).text()
        return r_type, r_id

    def edit_selected(self):
        """Edit the currently selected record in the table.
        :return: None """
        r_type, r_id = self._get_selected_record()
        if not r_type:
            QtWidgets.QMessageBox.warning(self, "Edit", "Select a row first.")
            return

       
        if r_type == "Student":
            obj = self.db.students[r_id]
            fields = [("Name", obj.name), ("Age", str(obj.age)), ("Email", obj._email), ("Student ID", obj.student_id)]
        elif r_type == "Instructor":
            obj = self.db.instructors[r_id]
            fields = [("Name", obj.name), ("Age", str(obj.age)), ("Email", obj._email), ("Instructor ID", obj.instructor_id)]
        else:  
            obj = self.db.courses[r_id]
            instr_val = obj.instructor.instructor_id if obj.instructor else ""
            fields = [("Course ID", obj.course_id), ("Course Name", obj.course_name), ("Instructor ID", instr_val)]

        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle(f"Edit {r_type}")
        form = QtWidgets.QFormLayout(dlg)
        edits = {}
        for label, value in fields:
            le = QtWidgets.QLineEdit(str(value))
            edits[label] = le
            form.addRow(label, le)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        form.addRow(btns)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)

        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return

        try:
            if r_type == "Student":
                new_name  = edits["Name"].text().strip()
                new_age   = validate_nonneg_int(edits["Age"].text().strip(), "Age")
                new_email = edits["Email"].text().strip()
                validate_email(new_email)
                new_id    = edits["Student ID"].text().strip()

                new = Student(new_name, new_age, new_email, new_id)
                self.db.update_student(r_id, new)

            elif r_type == "Instructor":
                new_name  = edits["Name"].text().strip()
                new_age   = validate_nonneg_int(edits["Age"].text().strip(), "Age")
                new_email = edits["Email"].text().strip()
                validate_email(new_email)
                new_id    = edits["Instructor ID"].text().strip()

                new = Instructor(new_name, new_age, new_email, new_id)
                self.db.update_instructor(r_id, new)

            else:  
                new_cid   = edits["Course ID"].text().strip()
                new_cname = edits["Course Name"].text().strip()
                iid       = edits["Instructor ID"].text().strip()
                instr     = self.db.instructors.get(iid) if iid else None

                new = Course(new_cid, new_cname, instr)
                self.db.update_course(r_id, new)

            self.refresh_all()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def delete_selected(self):
        """Delete the currently selected record in the table.
        :return: None """
        r_type, r_id = self._get_selected_record()
        if not r_type:
            QtWidgets.QMessageBox.warning(self, "Delete", "Select a row first.")
            return
        if QtWidgets.QMessageBox.question(
            self, "Confirm", f"Delete this {r_type} ({r_id})?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        ) != QtWidgets.QMessageBox.Yes:
            return

        try:
            if r_type == "Student":
                self.db.delete_student(r_id)
            elif r_type == "Instructor":
                self.db.delete_instructor(r_id)
            else:
                self.db.delete_course(r_id)

            self.refresh_all()
            QtWidgets.QMessageBox.information(self, "Deleted", f"{r_type} deleted.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))



# TODO: Add Help > About dialog (PyQt)
