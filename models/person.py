from __future__ import annotations
from .validators import validate_age, validate_email

class Person:
    """Class representing a person with basic attributes and validation.
     This class includes methods for initialization, introduction, and serialization.
     Attributes:
         name (str): The name of the person.
         age (int): The age of the person, must be a positive integer.
         _email (str): The email address of the person, must be a valid email format.
         Args:
             name (str): The name of the person.
             age (int): The age of the person.
             email (str): The email address of the person."""
    def __init__(self, name: str, age: int, email: str):
        validate_age(age)
        validate_email(email)
        self.name = name
        self.age = age
        self._email = email

    def introduce(self) -> None:
        """Prints a simple introduction message.
        Returns:
        str: A greeting message including the person's name and age."""
        print(f"Hello, my name is {self.name}, I am {self.age} years old.")

    def to_dict(self) -> dict:
        return {"name": self.name, "age": self.age, "email": self._email}

    @classmethod
    def from_dict(cls, d: dict) -> "Person":
        return cls(d["name"], int(d["age"]), d["email"])

