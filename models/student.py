from __future__ import annotations
from typing import List, TYPE_CHECKING
from .person import Person
if TYPE_CHECKING:
    from .course import Course

class Student(Person):
    """Class representing a student, inheriting from Person.
    Inherits attributes and methods from Person and adds student-specific attributes and methods.
    Attributes:
        student_id (str): The unique identifier for the student.
        registered_courses (List[Course]): List of courses the student is registered in.
        Args:
            name (str): The name of the student.
            age (int): The age of the student.
            email (str): The email address of the student.
            student_id (str): The unique identifier for the student."""
    def __init__(self, name: str, age: int, email: str, student_id: str):
        super().__init__(name, age, email)
        self.student_id = student_id
        self.registered_courses: List["Course"] = []

    def register_course(self, course: "Course"):
        """Registers the student for a course if not already registered.
        The method checks if the course is already in the student's registered courses list before adding it.
        Args:
            course (Course): The course to register the student in."""
        if course not in self.registered_courses:
            self.registered_courses.append(course)

    def to_dict(self) -> dict:
        """Serializes the student object to a dictionary, including inherited attributes.
        Returns:
            dict: A dictionary representation of the student object."""
        base = super().to_dict()
        base.update({
            "student_id": self.student_id,
            "registered_course_ids": [c.course_id for c in self.registered_courses],
        })
        return base

    @classmethod
    def from_dict(cls, d: dict) -> "Student":
        return cls(d["name"], int(d["age"]), d["email"], d["student_id"])
