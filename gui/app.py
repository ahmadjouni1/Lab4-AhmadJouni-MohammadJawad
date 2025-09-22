from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from data.db_sqlite import SchoolDBSqlite  # NEW
from models.student import Student
from models.instructor import Instructor
from models.course import Course

class SchoolApp(tk.Tk):
    def __init__(self, db: SchoolDBSqlite):
        super().__init__()
        self.title("School Management System")
        self.geometry("980x620")
        self.db = db
        self._make_menu()
        self._make_tabs()
        self.refresh_all()

    def _make_menu(self):
        menubar = tk.Menu(self)
        fmenu = tk.Menu(menubar, tearoff=0)
        fmenu.add_command(label="Open Database…", command=self.on_open_db)     
        fmenu.add_command(label="Backup Database…", command=self.on_backup_db) 
        fmenu.add_separator()
        fmenu.add_command(label="Load JSON…", command=self.on_load_json)
        fmenu.add_command(label="Save JSON…", command=self.on_save_json)
        fmenu.add_separator()
        fmenu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=fmenu)
        self.config(menu=menubar)

    def on_open_db(self):
        path = filedialog.asksaveasfilename(defaultextension=".db",
                                            filetypes=[("SQLite DB", "*.db"), ("All Files", "*.*")])
        if not path: return
        try:
            self.db.close()
        except Exception:
            pass
        self.db = SchoolDBSqlite(path)
        self.refresh_all()
        messagebox.showinfo("Database", f"Connected to:\n{path}")

    def on_backup_db(self):
        path = filedialog.asksaveasfilename(defaultextension=".db",
                                            filetypes=[("SQLite DB", "*.db")])
        if not path: return
        try:
            self.db.backup_db(path)
            messagebox.showinfo("Backup", f"Database copied to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_load_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path: return
        try:
            
            self.db = SchoolDBSqlite.load_json(path, getattr(self.db, "db_path", "school.db"))
            self.refresh_all()
            messagebox.showinfo("Loaded", f"Loaded JSON into database:\n{self.db.db_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_save_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON files", "*.json")])
        if not path: return
        try:
            self.db.save_json(path)
            messagebox.showinfo("Saved", f"Saved JSON:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    
    def _make_tabs(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_add = ttk.Frame(nb)
        self.tab_enroll = ttk.Frame(nb)
        self.tab_view = ttk.Frame(nb)

        nb.add(self.tab_add, text="Add Records")
        nb.add(self.tab_enroll, text="Registration & Assignment")
        nb.add(self.tab_view, text="View / Search")

        self._build_add_tab()
        self._build_enroll_tab()
        self._build_view_tab()


    def _build_add_tab(self):
        
        fs = ttk.LabelFrame(self.tab_add, text="Add Student")
        fs.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.st_name = ttk.Entry(fs); self._labeled(fs, "Name", 0, self.st_name)
        self.st_age  = ttk.Entry(fs); self._labeled(fs, "Age", 1, self.st_age)
        self.st_email= ttk.Entry(fs); self._labeled(fs, "Email", 2, self.st_email)
        self.st_id   = ttk.Entry(fs); self._labeled(fs, "Student ID", 3, self.st_id)
        ttk.Button(fs, text="Add Student", command=self.add_student).grid(row=4, column=1, sticky="e", pady=5)

        
        fi = ttk.LabelFrame(self.tab_add, text="Add Instructor")
        fi.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.ins_name = ttk.Entry(fi); self._labeled(fi, "Name", 0, self.ins_name)
        self.ins_age  = ttk.Entry(fi); self._labeled(fi, "Age", 1, self.ins_age)
        self.ins_email= ttk.Entry(fi); self._labeled(fi, "Email", 2, self.ins_email)
        self.ins_id   = ttk.Entry(fi); self._labeled(fi, "Instructor ID", 3, self.ins_id)
        ttk.Button(fi, text="Add Instructor", command=self.add_instructor).grid(row=4, column=1, sticky="e", pady=5)

        
        fc = ttk.LabelFrame(self.tab_add, text="Add Course")
        fc.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.c_id   = ttk.Entry(fc); self._labeled(fc, "Course ID", 0, self.c_id)
        self.c_name = ttk.Entry(fc); self._labeled(fc, "Course Name", 1, self.c_name)
        self.c_instr= ttk.Combobox(fc, state="readonly"); self._labeled(fc, "Instructor", 2, self.c_instr)
        ttk.Button(fc, text="Add Course", command=self.add_course).grid(row=3, column=1, sticky="e", pady=5)

        self.tab_add.columnconfigure((0,1), weight=1)

    def _labeled(self, parent, text, row, widget):
        ttk.Label(parent, text=text).grid(row=row, column=0, sticky="w", padx=4, pady=4)
        widget.grid(row=row, column=1, sticky="ew", padx=4, pady=4)
        parent.columnconfigure(1, weight=1)

    def add_student(self):
        try:
            s = Student(self.st_name.get().strip(),
                        int(self.st_age.get().strip()),
                        self.st_email.get().strip(),
                        self.st_id.get().strip())
            self.db.add_student(s)
            messagebox.showinfo("OK", "Student added.")
            self.st_name.delete(0, tk.END); self.st_age.delete(0, tk.END)
            self.st_email.delete(0, tk.END); self.st_id.delete(0, tk.END)
            self.refresh_all()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_instructor(self):
        try:
            ins = Instructor(self.ins_name.get().strip(),
                             int(self.ins_age.get().strip()),
                             self.ins_email.get().strip(),
                             self.ins_id.get().strip())
            self.db.add_instructor(ins)
            messagebox.showinfo("OK", "Instructor added.")
            self.ins_name.delete(0, tk.END); self.ins_age.delete(0, tk.END)
            self.ins_email.delete(0, tk.END); self.ins_id.delete(0, tk.END)
            self.refresh_all()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_course(self):
        try:
            instr_id = self.c_instr.get().split(" | ")[0] if self.c_instr.get() else None
            instr = self.db.instructors.get(instr_id) if instr_id else None
            c = Course(self.c_id.get().strip(), self.c_name.get().strip(), instr)
            self.db.add_course(c)
            messagebox.showinfo("OK", "Course added.")
            self.c_id.delete(0, tk.END); self.c_name.delete(0, tk.END); self.c_instr.set("")
            self.refresh_all()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    
    def _build_enroll_tab(self):
        fr = ttk.LabelFrame(self.tab_enroll, text="Student Registration")
        fr.pack(fill="x", padx=10, pady=10)
        self.reg_student = ttk.Combobox(fr, state="readonly", width=40)
        self.reg_course  = ttk.Combobox(fr, state="readonly", width=40)
        ttk.Label(fr, text="Student").grid(row=0, column=0, padx=5, pady=4, sticky="w")
        self.reg_student.grid(row=0, column=1, padx=5, pady=4)
        ttk.Label(fr, text="Course").grid(row=1, column=0, padx=5, pady=4, sticky="w")
        self.reg_course.grid(row=1, column=1, padx=5, pady=4)
        ttk.Button(fr, text="Register", command=self.register_student).grid(row=0, column=2, rowspan=2, padx=8)

        fa = ttk.LabelFrame(self.tab_enroll, text="Instructor Assignment")
        fa.pack(fill="x", padx=10, pady=10)
        self.ass_course = ttk.Combobox(fa, state="readonly", width=40)
        self.ass_instr  = ttk.Combobox(fa, state="readonly", width=40)
        ttk.Label(fa, text="Course").grid(row=0, column=0, padx=5, pady=4, sticky="w")
        self.ass_course.grid(row=0, column=1, padx=5, pady=4)
        ttk.Label(fa, text="Instructor").grid(row=1, column=0, padx=5, pady=4, sticky="w")
        self.ass_instr.grid(row=1, column=1, padx=5, pady=4)
        ttk.Button(fa, text="Assign", command=self.assign_instructor).grid(row=0, column=2, rowspan=2, padx=8)

    def register_student(self):
        try:
            sid = self.reg_student.get().split(" | ")[0]
            cid = self.reg_course.get().split(" | ")[0]
            self.db.register_student_in_course(sid, cid)
            messagebox.showinfo("OK", "Student registered to course.")
            self.refresh_all()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def assign_instructor(self):
        try:
            cid = self.ass_course.get().split(" | ")[0]
            iid = self.ass_instr.get().split(" | ")[0]
            self.db.assign_instructor_to_course(iid, cid)
            messagebox.showinfo("OK", "Instructor assigned to course.")
            self.refresh_all()
        except Exception as e:
            messagebox.showerror("Error", str(e))

  
    def _build_view_tab(self):
        top = ttk.Frame(self.tab_view); top.pack(fill="x", padx=10, pady=6)
        ttk.Label(top, text="Search").pack(side="left", padx=4)
        self.search_var = tk.StringVar()
        ent = ttk.Entry(top, textvariable=self.search_var, width=40)
        ent.pack(side="left", padx=4)
        ttk.Button(top, text="Go", command=self.on_search).pack(side="left", padx=4)
        ttk.Button(top, text="Clear", command=self.on_clear).pack(side="left", padx=4)

        cols = ("Type", "ID", "Name", "Extra")
        self.tree = ttk.Treeview(self.tab_view, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=210 if c == "Extra" else 160, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)

       
        btns = ttk.Frame(self.tab_view)
        btns.pack(fill="x", padx=10, pady=4)
        ttk.Button(btns, text="Edit Selected", command=self.edit_selected).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=4)

    def on_search(self):
        query = self.search_var.get().strip()
        res = self.db.search(query)
        self._fill_tree(res)

    def on_clear(self):
        self.search_var.set("")
        self.refresh_tree()

    def refresh_all(self):
        self.db.refresh_cache()  
        self.c_instr["values"] = [f"{i.instructor_id} | {i.name}" for i in self.db.instructors.values()]
        self.reg_student["values"] = [f"{s.student_id} | {s.name}" for s in self.db.students.values()]
        self.reg_course["values"]  = [f"{c.course_id} | {c.course_name}" for c in self.db.courses.values()]
        self.ass_course["values"]  = self.reg_course["values"]
        self.ass_instr["values"]   = self.c_instr["values"]
        self.refresh_tree()

    def refresh_tree(self):
        res = {"students": list(self.db.students.values()),
               "instructors": list(self.db.instructors.values()),
               "courses": list(self.db.courses.values())}
        self._fill_tree(res)

    def _fill_tree(self, res):
        self.tree.delete(*self.tree.get_children())
        
        for s in res["students"]:
            extra = ", ".join([c.course_id for c in s.registered_courses]) or "-"
            self.tree.insert("", "end", values=("Student", s.student_id, s.name, extra))
        
        for i in res["instructors"]:
            extra = ", ".join([c.course_id for c in i.assigned_courses]) or "-"
            self.tree.insert("", "end", values=("Instructor", i.instructor_id, i.name, extra))
        
        for c in res["courses"]:
            extra = f"Instr: {c.instructor.name if c.instructor else '—'}, Enrolled: {len(c.enrolled_students)}"
            self.tree.insert("", "end", values=("Course", c.course_id, c.course_name, extra))

    def _get_selected_record(self):
        sel = self.tree.selection()
        if not sel:
            return None, None
        row = self.tree.item(sel[0])["values"]
        return row[0], row[1]

    def edit_selected(self):
        r_type, r_id = self._get_selected_record()
        if not r_type:
            messagebox.showwarning("Edit", "Select a row first.")
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

        win = tk.Toplevel(self); win.title(f"Edit {r_type}")
        entries = {}
        for i, (label, value) in enumerate(fields):
            ttk.Label(win, text=label).grid(row=i, column=0, padx=6, pady=4, sticky="w")
            e = ttk.Entry(win); e.insert(0, value)
            e.grid(row=i, column=1, padx=6, pady=4, sticky="ew")
            entries[label] = e
        win.columnconfigure(1, weight=1)

        def on_save():
            try:
                if r_type == "Student":
                    new = Student(entries["Name"].get().strip(),
                                  int(entries["Age"].get().strip()),
                                  entries["Email"].get().strip(),
                                  entries["Student ID"].get().strip())
                    self.db.update_student(r_id, new)
                elif r_type == "Instructor":
                    new = Instructor(entries["Name"].get().strip(),
                                     int(entries["Age"].get().strip()),
                                     entries["Email"].get().strip(),
                                     entries["Instructor ID"].get().strip())
                    self.db.update_instructor(r_id, new)
                else:
                    iid = entries["Instructor ID"].get().strip()
                    instr = self.db.instructors.get(iid) if iid else None
                    new = Course(entries["Course ID"].get().strip(),
                                 entries["Course Name"].get().strip(),
                                 instr)
                    self.db.update_course(r_id, new)

                self.refresh_all()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win, text="Save", command=on_save).grid(row=len(fields), column=1, sticky="e", padx=6, pady=8)

    def delete_selected(self):
        r_type, r_id = self._get_selected_record()
        if not r_type:
            messagebox.showwarning("Delete", "Select a row first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete this {r_type} ({r_id})?"):
            return
        try:
            if r_type == "Student":
                self.db.delete_student(r_id)
            elif r_type == "Instructor":
                self.db.delete_instructor(r_id)
            else:
                self.db.delete_course(r_id)
            self.refresh_all()
            messagebox.showinfo("Deleted", f"{r_type} deleted.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
