import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def validate_email(email: str) -> None:
    """Validates the format of an email address.
    Raises a ValueError if the email format is invalid.
    Args:
        email (str): The email address to validate.
    """
    if not EMAIL_RE.match(email or ""):
        raise ValueError("Invalid email format.")

def validate_age(age: int) -> None:
    """Validates the age of a person.
    Raises a ValueError if the age is not a non-negative integer.
    Args:
        age (int): The age to validate.
    """
    if not isinstance(age, int) or age < 0:
        raise ValueError("Age must be a non-negative integer.")
