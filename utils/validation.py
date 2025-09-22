import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def validate_email(email: str) -> None:
    if not EMAIL_RE.match(email or ""):
        raise ValueError("Invalid email format")

def validate_age(age: int) -> None:
    if not isinstance(age, int) or age < 0:
        raise ValueError("Age must be a non-negative integer")
