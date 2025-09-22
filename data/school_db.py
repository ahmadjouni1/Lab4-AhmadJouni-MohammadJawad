from __future__ import annotations
import json
from typing import Dict, List
from models.student import Student
from models.instructor import Instructor
from models.course import Course

class SchoolDB:
    def __init__(self):
        self.students: Dict[str, Student] = {}
        self.instructors: Dict[str, Instructor] = {}
        self.courses: Dict[str, Course] = {}

    def add_student(self, s: Student):
        self.students[s.student_id] = s

    def add_instructor(self, i: Instructor):
        self.instructors[i.instructor_id] = i

    def add_course(self, c: Course):
        self.courses[c.course_id] = c

  
    def register_student_in_course(self, student_id: str, course_id: str):
        s = self.students[student_id]
        c = self.courses[course_id]
        c.add_student(s)
        s.register_course(c)

    def assign_instructor_to_course(self, instructor_id: str, course_id: str):
        i = self.instructors[instructor_id]
        c = self.courses[course_id]
        c.instructor = i
        i.assign_course(c)

  
    def search(self, text: str) -> Dict[str, List]:
        t = (text or "").lower()
        res = {
            "students": [s for s in self.students.values()
                         if t in s.name.lower() or t in s.student_id.lower()],
            "instructors": [i for i in self.instructors.values()
                            if t in i.name.lower() or t in i.instructor_id.lower()],
            "courses": [c for c in self.courses.values()
                        if t in c.course_name.lower() or t in c.course_id.lower()],
        }
        return res

   
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
    def load_json(cls, path: str) -> "SchoolDB":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        db = cls()
        for sd in data.get("students", []):
            db.add_student(Student.from_dict(sd))
        for idd in data.get("instructors", []):
            db.add_instructor(Instructor.from_dict(idd))

        
        for cd in data.get("courses", []):
            instr = db.instructors.get(cd.get("instructor_id")) if cd.get("instructor_id") else None
            course = Course.from_dict(cd, instr)
            db.add_course(course)
            if instr:
                instr.assign_course(course)

      
        for cd in data.get("courses", []):
            c = db.courses[cd["course_id"]]
            for sid in cd.get("enrolled_student_ids", []):
                if sid in db.students:
                    db.register_student_in_course(sid, c.course_id)

        for sd in data.get("students", []):
            s = db.students[sd["student_id"]]
            for cid in sd.get("registered_course_ids", []):
                if cid in db.courses and db.courses[cid] not in s.registered_courses:
                    s.register_course(db.courses[cid])

        return db
