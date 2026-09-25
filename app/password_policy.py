"""
A simple, dependency-free password strength check. Used anywhere a new
password is set: registration, reset-password, and change-password.
"""

import re

MIN_LENGTH = 8

REQUIREMENTS_TEXT = (
    f"At least {MIN_LENGTH} characters, with an uppercase letter, a lowercase "
    "letter, a number, and a symbol (e.g. ! @ # $ %)."
)


def validate_password_strength(password):
    """Return (is_valid, message). message explains what's missing when invalid."""
    password = password or ""
    issues = []

    if len(password) < MIN_LENGTH:
        issues.append(f"at least {MIN_LENGTH} characters")
    if not re.search(r"[a-z]", password):
        issues.append("a lowercase letter")
    if not re.search(r"[A-Z]", password):
        issues.append("an uppercase letter")
    if not re.search(r"[0-9]", password):
        issues.append("a number")
    if not re.search(r"[^A-Za-z0-9]", password):
        issues.append("a symbol (e.g. ! @ # $ %)")

    if issues:
        return False, "Password must include " + ", ".join(issues) + "."
    return True, ""
