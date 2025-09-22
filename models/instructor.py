from __future__ import annotations
from typing import List, TYPE_CHECKING
from .person import Person
if TYPE_CHECKING:
    from .course import Course 

class Instructor(Person):
    """Class representing an instructor, inheriting from Person.
    Inherits attributes and methods from Person and adds instructor-specific attributes and methods.
    Attributes:
        instructor_id (str): The unique identifier for the instructor.
        assigned_courses (List[Course]): List of courses the instructor is assigned to.
        Args:
            name (str): The name of the instructor.
            age (int): The age of the instructor.
            email (str): The email address of the instructor.
            instructor_id (str): The unique identifier for the instructor."""
    def __init__(self, name: str, age: int, email: str, instructor_id: str):
        super().__init__(name, age, email)
        self.instructor_id = instructor_id
        self.assigned_courses = []

    def assign_course(self, course: "Course"):
        """Assigns the instructor to a course if not already assigned.
        The method checks if the course is already in the instructor's assigned courses list before adding it"""
        if course not in self.assigned_courses:
            self.assigned_courses.append(course)

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "instructor_id": self.instructor_id,
            "assigned_course_ids": [c.course_id for c in self.assigned_courses],
        })
        return base

    @classmethod
    def from_dict(cls, d: dict) -> "Instructor":
        return cls(d["name"], int(d["age"]), d["email"], d["instructor_id"])
