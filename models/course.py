from __future__ import annotations
from typing import List
from .instructor import Instructor
from .student import Student

class Course:
    """Class representing a course with attributes and methods for managing enrolled students and instructor.
    Attributes: 
    course_id (str): The unique identifier for the course.
    course_name (str): The name of the course.
    instructor (Instructor | None): The instructor assigned to the course, can be None.
    enrolled_students (List[Student]): List of students enrolled in the course.
    Args:
        course_id (str): The unique identifier for the course.
        course_name (str): The name of the course.
        instructor (Instructor | None): The instructor assigned to the course, can be None."""
    def __init__(self, course_id: str, course_name: str, instructor: Instructor | None):
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor
        self.enrolled_students: List[Student] = []

    def add_student(self, student: Student):
        """Adds a student to the course if not already enrolled.
        The method checks if the student is already in the enrolled students list before adding them."""
        if student not in self.enrolled_students:
            self.enrolled_students.append(student)

    def to_dict(self) -> dict:
        """Serializes the course object to a dictionary, including relevant attributes.
        Returns:
            dict: A dictionary representation of the course object."""
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "instructor_id": self.instructor.instructor_id if self.instructor else None,
            "enrolled_student_ids": [s.student_id for s in self.enrolled_students],
        }

    @classmethod
    def from_dict(cls, d: dict, instructor: Instructor | None) -> "Course":
        return cls(d["course_id"], d["course_name"], instructor)

    def __str__(self) -> str:
        return f"{self.course_id} - {self.course_name}" + \
               (f" (Instructor: {self.instructor.name})" if self.instructor else "")

