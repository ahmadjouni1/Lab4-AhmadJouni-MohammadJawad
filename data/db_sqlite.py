from __future__ import annotations
import os, sqlite3, shutil, json
from typing import Dict, List, Optional
from models.student import Student
from models.instructor import Instructor
from models.course import Course

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
  student_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  age INTEGER NOT NULL CHECK (age >= 0),
  email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS instructors (
  instructor_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  age INTEGER NOT NULL CHECK (age >= 0),
  email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
  course_id TEXT PRIMARY KEY,
  course_name TEXT NOT NULL,
  instructor_id TEXT NULL,
  FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS registrations (
  student_id TEXT NOT NULL,
  course_id TEXT NOT NULL,
  PRIMARY KEY (student_id, course_id),
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  FOREIGN KEY (course_id)  REFERENCES courses(course_id)  ON DELETE CASCADE
);
"""

class SchoolDBSqlite:
    def view_rows(self):
        """Yield tuples for the table view: (type, id, name, age, email, courses_or_instructor)"""
        # Students
        for s in self.students.values():
            courses = ", ".join(c.course_id for c in getattr(s, 'registered_courses', []))
            yield ("Student", s.student_id, s.name, s.age, getattr(s, '_email', getattr(s, 'email', '')), courses)
        # Instructors
        for i in self.instructors.values():
            courses = ", ".join(c.course_id for c in getattr(i, 'assigned_courses', []))
            yield ("Instructor", i.instructor_id, i.name, i.age, getattr(i, '_email', getattr(i, 'email', '')), courses)
        # Courses
        for c in self.courses.values():
            instr = c.instructor.name if c.instructor else ""
            yield ("Course", c.course_id, c.course_name, "", "", instr)
    def get_students(self):
        """Return a list of students as dicts."""
        return [s.to_dict() for s in self.students.values()]

    def get_instructors(self):
        """Return a list of instructors as dicts."""
        return [i.to_dict() for i in self.instructors.values()]

    def get_courses(self):
        """Return a list of courses as dicts."""
        return [c.to_dict() for c in self.courses.values()]
    """
    SQLite-backed DB with an in-memory object cache to keep GUI code simple.
    Exposes the same attributes/methods the GUIs already use:
      - students / instructors / courses  (dicts)
      - add_student / add_instructor / add_course
      - register_student_in_course / assign_instructor_to_course
      - search()
      - save_json(path) / load_json(path)
      - backup_db(path)
    """
    def __init__(self, db_path: str = "school.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._ensure_schema()
    
        self.students: Dict[str, Student] = {}
        self.instructors: Dict[str, Instructor] = {}
        self.courses: Dict[str, Course] = {}
        self.refresh_cache()

    
    def _ensure_schema(self):
        cur = self.conn.cursor()
        cur.executescript(SCHEMA)
        self.conn.commit()

    
    def refresh_cache(self):
        self.students.clear()
        self.instructors.clear()
        self.courses.clear()

        cur = self.conn.cursor()

        
        for sid, name, age, email in cur.execute("SELECT student_id,name,age,email FROM students"):
            self.students[sid] = Student(name, int(age), email, sid)

        for iid, name, age, email in cur.execute("SELECT instructor_id,name,age,email FROM instructors"):
            self.instructors[iid] = Instructor(name, int(age), email, iid)


        for cid, cname, iid in cur.execute("SELECT course_id,course_name,instructor_id FROM courses"):
            instr = self.instructors.get(iid) if iid else None
            self.courses[cid] = Course(cid, cname, instr)

        
        for i in self.instructors.values():
            i.assigned_courses.clear()
        for c in self.courses.values():
            if c.instructor:
                c.instructor.assign_course(c)

        
        for c in self.courses.values():
            c.enrolled_students.clear()
        for sid, cid in cur.execute("SELECT student_id, course_id FROM registrations"):
            s = self.students.get(sid)
            c = self.courses.get(cid)
            if s and c:
                if c not in s.registered_courses:
                    s.register_course(c)
                if s not in c.enrolled_students:
                    c.enrolled_students.append(s)

    
    def add_student(self, s: Student):
        self.conn.execute(
            "INSERT INTO students(student_id,name,age,email) VALUES (?,?,?,?)",
            (s.student_id, s.name, s.age, s._email),
        )
        self.conn.commit()
        self.refresh_cache()

    
    def add_instructor(self, i: Instructor):
        self.conn.execute(
            "INSERT INTO instructors(instructor_id,name,age,email) VALUES (?,?,?,?)",
            (i.instructor_id, i.name, i.age, i._email),
        )
        self.conn.commit()
        self.refresh_cache()

    
    def add_course(self, c: Course):
        iid = c.instructor.instructor_id if c.instructor else None
        self.conn.execute(
            "INSERT INTO courses(course_id,course_name,instructor_id) VALUES (?,?,?)",
            (c.course_id, c.course_name, iid),
        )
        self.conn.commit()
        self.refresh_cache()

    
    def register_student_in_course(self, student_id: str, course_id: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO registrations(student_id, course_id) VALUES (?,?)",
            (student_id, course_id),
        )
        self.conn.commit()
        self.refresh_cache()

    def assign_instructor_to_course(self, instructor_id: str, course_id: str):
        self.conn.execute(
            "UPDATE courses SET instructor_id=? WHERE course_id=?",
            (instructor_id, course_id),
        )
        self.conn.commit()
        self.refresh_cache()

    
    def search(self, text: str) -> Dict[str, List]:
        t = (text or "").lower()
        
        res = {
            "students": [s for s in self.students.values() if t in s.name.lower() or t in s.student_id.lower()],
            "instructors": [i for i in self.instructors.values() if t in i.name.lower() or t in i.instructor_id.lower()],
            "courses": [c for c in self.courses.values() if t in c.course_name.lower() or t in c.course_id.lower()],
        }
        return res

    
    def delete_student(self, student_id: str):
        self.conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
        self.conn.commit()
        self.refresh_cache()

    def delete_instructor(self, instructor_id: str):
        self.conn.execute("DELETE FROM instructors WHERE instructor_id=?", (instructor_id,))
        self.conn.commit()
        self.refresh_cache()

    def delete_course(self, course_id: str):
        self.conn.execute("DELETE FROM courses WHERE course_id=?", (course_id,))
        self.conn.commit()
        self.refresh_cache()

  
    def update_student(self, old_id: str, s: Student):
        cur = self.conn.cursor()
        
        if old_id != s.student_id:
            cur.execute("UPDATE students SET student_id=? WHERE student_id=?", (s.student_id, old_id))
           
            cur.execute("UPDATE registrations SET student_id=? WHERE student_id=?", (s.student_id, old_id))
        cur.execute("UPDATE students SET name=?, age=?, email=? WHERE student_id=?",
                    (s.name, s.age, s._email, s.student_id))
        self.conn.commit()
        self.refresh_cache()

    def update_instructor(self, old_id: str, i: Instructor):
        cur = self.conn.cursor()
        if old_id != i.instructor_id:
            cur.execute("UPDATE instructors SET instructor_id=? WHERE instructor_id=?", (i.instructor_id, old_id))
            cur.execute("UPDATE courses SET instructor_id=? WHERE instructor_id=?", (i.instructor_id, old_id))
        cur.execute("UPDATE instructors SET name=?, age=?, email=? WHERE instructor_id=?",
                    (i.name, i.age, i._email, i.instructor_id))
        self.conn.commit()
        self.refresh_cache()

    def update_course(self, old_id: str, c: Course):
        cur = self.conn.cursor()
        if old_id != c.course_id:
            cur.execute("UPDATE registrations SET course_id=? WHERE course_id=?", (c.course_id, old_id))
        iid = c.instructor.instructor_id if c.instructor else None
        cur.execute("UPDATE courses SET course_id=?, course_name=?, instructor_id=? WHERE course_id=?",
                    (c.course_id, c.course_name, iid, old_id))
        self.conn.commit()
        self.refresh_cache()

    
    def to_dict(self) -> dict:
        return {
            "students": [s.to_dict() for s in self.students.values()],
            "instructors": [i.to_dict() for i in self.instructors.values()],
            "courses": [c.to_dict() for c in self.courses.values()],
        }

    def save_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_json(cls, path: str, db_path: str = "school.db") -> "SchoolDBSqlite":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        db = cls(db_path)
        
        cur = db.conn.cursor()
        cur.executescript("""
            DELETE FROM registrations;
            DELETE FROM courses;
            DELETE FROM students;
            DELETE FROM instructors;
        """)
        
        for sd in data.get("students", []):
            s = Student.from_dict(sd)
            db.add_student(s)
        
        for idd in data.get("instructors", []):
            i = Instructor.from_dict(idd)
            db.add_instructor(i)
       
        for cd in data.get("courses", []):
            instr = db.instructors.get(cd.get("instructor_id")) if cd.get("instructor_id") else None
            c = Course.from_dict(cd, instr)
            db.add_course(c)
       
        for cd in data.get("courses", []):
            for sid in cd.get("enrolled_student_ids", []):
                if sid in db.students:
                    db.register_student_in_course(sid, cd["course_id"])
        db.refresh_cache()
        return db

    
    def backup_db(self, dest_path: str):
        
        self.conn.commit()
        shutil.copy2(self.db_path, dest_path)

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass
