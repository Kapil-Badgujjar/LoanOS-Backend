from pydantic import BaseModel, Field
from datetime import date


class ApplicationCreate(BaseModel):
    full_name: str
    mobile: str
    pan: str
    dob: date
    employment_type: str = Field(pattern="^(Salaried|Self-Employed)$")
    monthly_income: float
    loan_amount: float
