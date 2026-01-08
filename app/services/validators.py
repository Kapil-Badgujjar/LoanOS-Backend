import re
from datetime import date


def validate_pan(pan: str):
    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
    return bool(re.match(pattern, pan))


def calculate_age(dob: date):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
