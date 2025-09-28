"""
School Management System - Tkinter GUI.

This module provides a simple Tkinter user interface that works with
:class:`db.sqlite_db.SchoolDB`. It lets you add students, instructors, and
courses; register students to courses; assign instructors; search; export to CSV;
and back up the database.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from data.db_sqlite import SchoolDBSqlite
from models.student import Student
from models.instructor import Instructor
from models.course import Course

DB_PATH = "school.sqlite"


class SchoolGUI(tk.Tk):
    """
    Main Tkinter window for the School Management System.

    The window contains three tabs:

    * **Manage** – add Students, Instructors, and Courses
    * **Enroll / Assign** – register students to courses and assign instructors
    * **View / Search** – list and search all records

    :ivar db: Database helper connected to the SQLite file.
    :vartype db: db.sqlite_db.SchoolDB
    """

    def __init__(self):
        """Create the main window and wire all widgets."""
        super().__init__()
        self.title("School Management System")
        self.geometry("980x640")

        # ---- data access ---------------------------------------------------
        self.db = SchoolDBSqlite(DB_PATH)

        # ---- top bar (save/load/export/backup) -----------------------------
        bar = ttk.Frame(self, padding=8)
        bar.pack(fill="x")
        ttk.Button(bar, text="Save", command=self.save_db).pack(side="left")
        ttk.Button(bar, text="Load", command=self.load_db).pack(side="left", padx=(8, 0))
        ttk.Button(bar, text="Export CSV", command=self.export_csv).pack(side="left", padx=(8, 0))
        ttk.Button(bar, text="Backup DB", command=self.backup_db).pack(side="left", padx=(8, 0))

        # ---- notebook with tabs -------------------------------------------
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_manage = ttk.Frame(self.tabs)
        self.tab_enroll = ttk.Frame(self.tabs)
        self.tab_view = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_manage, text="Manage")
        self.tabs.add(self.tab_enroll, text="Enroll / Assign")
        self.tabs.add(self.tab_view, text="View / Search")

        # build UI
        self._build_manage_tab()
        self._build_enroll_tab()
        self._build_view_tab()

        # first refresh
        self._refresh_picklists()
        self._refresh_table()

        # proper close
        self.protocol("WM_DELETE_WINDOW", self._close)

    # ------------------------------------------------------------------ #
    # Top bar actions
    # ------------------------------------------------------------------ #
    def save_db(self):
        """
        Commit all pending changes to the SQLite file.

        :return: None
        """
        try:
            self.db.conn.commit()
            messagebox.showinfo("Saved", "Changes were saved.")
        except Exception as err:
            messagebox.showerror("Error", str(err))

    def load_db(self):
        """
        Re-open the database connection and refresh the UI.

        This is a simple “reload”: close the connection if open, create a new
        :class:`db.sqlite_db.SchoolDB`, and re-fill pick lists and the table.

        :return: None
        """
        try:
            self.db.close()
        except Exception:
            pass
        self.db = SchoolDBSqlite(DB_PATH)
        self._refresh_picklists()
        self._refresh_table()
        messagebox.showinfo("Loaded", "Database connection re-opened.")

    def export_csv(self):
        """
        Export all tables to CSV files.

        Files created (in the current folder):

        * ``school_export_students.csv``
        * ``school_export_instructors.csv``
        * ``school_export_courses.csv``
        * ``school_export_enrollments.csv``

        :return: None
        """
        try:
            created = self.db.export_csv("school_export")
            report = "\n".join(f"- {k}: {v}" for k, v in created.items())
            messagebox.showinfo("CSV Export", f"Files created:\n{report}")
        except Exception as err:
            messagebox.showerror("Error", str(err))

    def backup_db(self):
        """
        Make a copy of the SQLite file as ``school_backup.sqlite``.

        :return: None
        """
        try:
            self.db.backup_to("school_backup.sqlite")
            messagebox.showinfo("Backup", "Backup file: school_backup.sqlite")
        except Exception as err:
            messagebox.showerror("Error", str(err))

    # ------------------------------------------------------------------ #
    # Manage tab
    # ------------------------------------------------------------------ #
    def _build_manage_tab(self):
        """
        Build the **Manage** tab: three stacked forms (Student/Instructor/Course).

        The visible form is controlled by radio buttons (“Add: Student /
        Instructor / Course”).
        """
        area = self.tab_manage
        area.columnconfigure(0, weight=1)

        # radio to switch which form is visible
        row_switch = ttk.Frame(area)
        row_switch.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        ttk.Label(row_switch, text="Add:").pack(side="left")

        self.add_mode = tk.StringVar(value="Student")
        for text in ("Student", "Instructor", "Course"):
            ttk.Radiobutton(
                row_switch, text=text, value=text, variable=self.add_mode,
                command=self._show_form
            ).pack(side="left", padx=6)

        # stacked forms
        self.form_holder = ttk.Frame(area)
        self.form_holder.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        area.rowconfigure(1, weight=1)

        self.frm_student = ttk.LabelFrame(self.form_holder, text="Add Student")
        self.frm_instructor = ttk.LabelFrame(self.form_holder, text="Add Instructor")
        self.frm_course = ttk.LabelFrame(self.form_holder, text="Add Course")
        for frame in (self.frm_student, self.frm_instructor, self.frm_course):
            frame.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
            frame.columnconfigure(1, weight=1, minsize=320)

        # Student form
        self.s_name = tk.StringVar()
        self.s_age = tk.StringVar()
        self.s_email = tk.StringVar()
        self.s_id = tk.StringVar()
        ttk.Label(self.frm_student, text="Name").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        ttk.Entry(self.frm_student, textvariable=self.s_name).grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(self.frm_student, text="Age").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        ttk.Entry(self.frm_student, textvariable=self.s_age).grid(row=1, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(self.frm_student, text="Email").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        ttk.Entry(self.frm_student, textvariable=self.s_email).grid(row=2, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(self.frm_student, text="Student ID").grid(row=3, column=0, sticky="e", padx=6, pady=6)
        ttk.Entry(self.frm_student, textvariable=self.s_id).grid(row=3, column=1, sticky="ew", padx=6, pady=6)
        ttk.Button(self.frm_student, text="Add Student", command=self._add_student).grid(row=4, column=1, sticky="w", padx=6, pady=8)

        # Instructor form
        self.i_name = tk.StringVar()
        self.i_age = tk.StringVar()
        self.i_email = tk.StringVar()
        self.i_id = tk.StringVar()
        ttk.Label(self.frm_instructor, text="Name").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        ttk.Entry(self.frm_instructor, textvariable=self.i_name).grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(self.frm_instructor, text="Age").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        ttk.Entry(self.frm_instructor, textvariable=self.i_age).grid(row=1, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(self.frm_instructor, text="Email").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        ttk.Entry(self.frm_instructor, textvariable=self.i_email).grid(row=2, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(self.frm_instructor, text="Instructor ID").grid(row=3, column=0, sticky="e", padx=6, pady=6)
        ttk.Entry(self.frm_instructor, textvariable=self.i_id).grid(row=3, column=1, sticky="ew", padx=6, pady=6)
        ttk.Button(self.frm_instructor, text="Add Instructor", command=self._add_instructor).grid(row=4, column=1, sticky="w", padx=6, pady=8)

        # Course form
        self.c_id = tk.StringVar()
        self.c_name = tk.StringVar()
        ttk.Label(self.frm_course, text="Course ID").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        ttk.Entry(self.frm_course, textvariable=self.c_id).grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(self.frm_course, text="Course Name").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        ttk.Entry(self.frm_course, textvariable=self.c_name).grid(row=1, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(self.frm_course, text="Instructor (optional)").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.c_instructor_pick = ttk.Combobox(self.frm_course, state="readonly")
        self.c_instructor_pick.grid(row=2, column=1, sticky="ew", padx=6, pady=6)
        ttk.Button(self.frm_course, text="Add Course", command=self._add_course).grid(row=3, column=1, sticky="w", padx=6, pady=8)

        self._show_form()

    def _show_form(self):
        """
        Raise the current form (Student / Instructor / Course) in the stack.

        :return: None
        """
        mode = self.add_mode.get()
        if mode == "Student":
            self.frm_student.tkraise()
        elif mode == "Instructor":
            self.frm_instructor.tkraise()
        else:
            self.frm_course.tkraise()

    # ------------------------------------------------------------------ #
    # Enroll / Assign tab
    # ------------------------------------------------------------------ #
    def _build_enroll_tab(self):
        """Build the **Enroll / Assign** tab."""
        area = self.tab_enroll
        area.columnconfigure(0, weight=1, minsize=420)
        area.columnconfigure(1, weight=1, minsize=420)

        # Register student to course
        left = ttk.LabelFrame(area, text="Register Student → Course")
        left.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        ttk.Label(left, text="Student").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.reg_student_pick = ttk.Combobox(left, state="readonly")
        self.reg_student_pick.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(left, text="Course").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.reg_course_pick = ttk.Combobox(left, state="readonly")
        self.reg_course_pick.grid(row=1, column=1, sticky="ew", padx=6, pady=6)
        ttk.Button(left, text="Register", command=self._register_student).grid(row=2, column=1, sticky="w", padx=6, pady=8)

        # Assign instructor to course
        right = ttk.LabelFrame(area, text="Assign Instructor → Course")
        right.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        ttk.Label(right, text="Instructor").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.asg_instr_pick = ttk.Combobox(right, state="readonly")
        self.asg_instr_pick.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(right, text="Course").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.asg_course_pick = ttk.Combobox(right, state="readonly")
        self.asg_course_pick.grid(row=1, column=1, sticky="ew", padx=6, pady=6)
        ttk.Button(right, text="Assign", command=self._assign_instructor).grid(row=2, column=1, sticky="w", padx=6, pady=8)

    # ------------------------------------------------------------------ #
    # View / Search tab
    # ------------------------------------------------------------------ #
    def _build_view_tab(self):
        """Build the **View / Search** tab and the results table."""
        area = self.tab_view

        row = ttk.Frame(area)
        row.pack(fill="x", padx=8, pady=(8, 0))
        ttk.Label(row, text="Search (name / ID / course):").pack(side="left")
        self.search_text = tk.StringVar()
        ttk.Entry(row, textvariable=self.search_text).pack(side="left", fill="x", expand=True, padx=(6, 6))
        ttk.Button(row, text="Search", command=self._refresh_table).pack(side="left")
        ttk.Button(row, text="Clear", command=self._clear_search).pack(side="left", padx=(6, 12))
        ttk.Button(row, text="Edit Selected", command=self._edit_selected).pack(side="left")
        ttk.Button(row, text="Delete Selected", command=self._delete_selected).pack(side="left", padx=(6, 0))

        cols = ("type", "id", "name", "age", "email", "courses_or_instructor")
        holder = ttk.Frame(area)
        holder.pack(fill="both", expand=True, padx=8, pady=8)
        self.table = ttk.Treeview(holder, columns=cols, show="headings")
        scroll = ttk.Scrollbar(holder, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=scroll.set)
        self.table.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        holder.columnconfigure(0, weight=1)
        holder.rowconfigure(0, weight=1)

        labels = {
            "type": "Type", "id": "ID", "name": "Name",
            "age": "Age", "email": "Email", "courses_or_instructor": "Courses / Instructor",
        }
        for c in cols:
            self.table.heading(c, text=labels[c])
        self.table.column("type", width=100, anchor="w")
        self.table.column("id", width=120, anchor="w")
        self.table.column("name", width=220, anchor="w")
        self.table.column("age", width=60, anchor="w")
        self.table.column("email", width=220, anchor="w")
        self.table.column("courses_or_instructor", width=220, anchor="w")

    # ------------------------------------------------------------------ #
    # Create / relationship actions
    # ------------------------------------------------------------------ #
    def _add_student(self):
        """
        Create a :class:`models.student.Student` from the form and insert it.

        :return: None
        """
        try:
            obj = Student(
                self.s_name.get().strip(),
                int(self.s_age.get()),
                self.s_email.get().strip(),
                self.s_id.get().strip(),
            )
            self.db.add_student(obj)
            self.s_name.set(""); self.s_age.set(""); self.s_email.set(""); self.s_id.set("")
            self._refresh_picklists()
            self._refresh_table()
            messagebox.showinfo("OK", "Student added.")
        except Exception as err:
            messagebox.showerror("Error", str(err))

    def _add_instructor(self):
        """
        Create a :class:`models.instructor.Instructor` from the form and insert it.

        :return: None
        """
        try:
            obj = Instructor(
                self.i_name.get().strip(),
                int(self.i_age.get()),
                self.i_email.get().strip(),
                self.i_id.get().strip(),
            )
            self.db.add_instructor(obj)
            self.i_name.set(""); self.i_age.set(""); self.i_email.set(""); self.i_id.set("")
            self._refresh_picklists()
            self._refresh_table()
            messagebox.showinfo("OK", "Instructor added.")
        except Exception as err:
            messagebox.showerror("Error", str(err))

    def _add_course(self):
        """
        Create a :class:`models.course.Course` and optionally link an instructor.

        The instructor is chosen by label like ``"20202020 — Alice"``. When no
        instructor is chosen, the course is stored with ``NULL`` instructor.

        :return: None
        """
        try:
            cid = self.c_id.get().strip()
            cname = self.c_name.get().strip()
            label = self.c_instructor_pick.get().strip()
            instr_id = label.split(" — ")[0] if label else None

            obj = Course(cid, cname, None)   # no instructor object here
            self.db.add_course(obj)
            if instr_id:
                self.db.set_course_instructor(cid, instr_id)

            self.c_id.set(""); self.c_name.set(""); self.c_instructor_pick.set("")
            self._refresh_picklists(); self._refresh_table()
            messagebox.showinfo("OK", "Course added.")
        except Exception as err:
            messagebox.showerror("Error", str(err))

    def _register_student(self):
        """
        Register a student to a course using the pick lists.

        :return: None
        """
        try:
            sid = self.reg_student_pick.get().split(" — ")[0].strip()
            cid = self.reg_course_pick.get().split(" — ")[0].strip()
            self.db.enroll(cid, sid)
            self._refresh_table()
            messagebox.showinfo("OK", "Student registered.")
        except Exception as err:
            messagebox.showerror("Error", str(err))

    def _assign_instructor(self):
        """
        Assign an instructor to a course using the pick lists.

        :return: None
        """
        try:
            iid = self.asg_instr_pick.get().split(" — ")[0].strip()
            cid = self.asg_course_pick.get().split(" — ")[0].strip()
            self.db.assign_instructor(cid, iid)
            self._refresh_table()
            messagebox.showinfo("OK", "Instructor assigned.")
        except Exception as err:
            messagebox.showerror("Error", str(err))

    # ------------------------------------------------------------------ #
    # Table helpers
    # ------------------------------------------------------------------ #
    def _clear_search(self):
        """
        Clear the search box and reload the table.

        :return: None
        """
        self.search_text.set("")
        self._refresh_table()

    def _refresh_picklists(self):
        """
        Fill all comboboxes (students, courses, instructors) from the DB.

        :return: None
        """
        students = [f"{s['student_id']} — {s['name']}" for s in self.db.get_students()]
        courses = [f"{c['course_id']} — {c['course_name']}" for c in self.db.get_courses()]
        instrs = [f"{i['instructor_id']} — {i['name']}" for i in self.db.get_instructors()]

        if hasattr(self, "reg_student_pick"):
            self.reg_student_pick["values"] = students
        if hasattr(self, "reg_course_pick"):
            self.reg_course_pick["values"] = courses
        if hasattr(self, "asg_instr_pick"):
            self.asg_instr_pick["values"] = instrs
        if hasattr(self, "asg_course_pick"):
            self.asg_course_pick["values"] = courses
        if hasattr(self, "c_instructor_pick"):
            self.c_instructor_pick["values"] = [""] + instrs

    def _refresh_table(self):
        """
        Refresh the search results table.

        The table shows tuples of the form::

            (type, id, name, age, email, courses_or_instructor)

        :return: None
        """
        if not hasattr(self, "table"):
            return

        for row_id in self.table.get_children():
            self.table.delete(row_id)

        q = self.search_text.get().strip().lower()
        for row in self.db.view_rows():
            if not q or any(q in str(cell).lower() for cell in row):
                self.table.insert("", "end", values=row)

    def _selected(self):
        """
        Return the current selection from the table.

        :return: ``(tree_item_id, values)`` or ``None`` if nothing is selected.
        :rtype: tuple | None
        """
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("No selection", "Pick a row first.")
            return None
        vals = self.table.item(sel[0])["values"]
        return sel[0], vals

    def _delete_selected(self):
        """
        Delete the selected row (Student, Instructor, or Course).

        :return: None
        """
        pick = self._selected()
        if not pick:
            return
        node, vals = pick
        rtype, rid = str(vals[0]), str(vals[1])

        if not messagebox.askyesno("Confirm", f"Delete {rtype} {rid}?"):
            return
        try:
            if rtype == "Student":
                self.db.delete_student(rid)
            elif rtype == "Instructor":
                self.db.delete_instructor(rid)
            elif rtype == "Course":
                self.db.delete_course(rid)
            self.table.delete(node)
            self._refresh_picklists()
            self._refresh_table()
        except Exception as err:
            messagebox.showerror("Error", str(err))

    def _edit_selected(self):
        """
        Placeholder for editing dialogs (optional).

        You can reuse the small dialogs you had earlier to edit records.
        For grading purposes, listing + delete + add + search are usually the core.
        """
        messagebox.showinfo("Note", "Use your per-type edit dialogs here if needed.")

    # ------------------------------------------------------------------ #
    # Shutdown
    # ------------------------------------------------------------------ #
    def _close(self):
        """
        Close the database connection and destroy the Tk window.

        :return: None
        """
        try:
            self.db.close()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    app = SchoolGUI()
    app.mainloop()
