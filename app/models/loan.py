from datetime import date
from typing import Literal
from pydantic import BaseModel, Field

LoanStatus = Literal['Pending','Active','Returned','Cancelled']
class LoanCreate(BaseModel):
    artifact_id: str
    institution_id: str
    loan_date: date
    expected_return_date: date
    actual_return_date: date | None = None
    status: LoanStatus = 'Pending'
    notes: str | None = None

class LoanUpdate(LoanCreate):
    pass
