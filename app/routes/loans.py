
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.services.loans import (
    get_all_loans,
    get_loan_by_id,
)

from datetime import date
from pydantic import BaseModel, Field
from app.services.loans import create_loan

router = APIRouter(
    prefix="/api/loans",
    tags=["Loans"]
)


@router.get("/")
def list_loans():
    """Return all museum loans."""
    return get_all_loans()


@router.get("/{loan_id}")
def loan_details(loan_id: UUID):
    """Return a specific museum loan."""
    loan = get_loan_by_id(str(loan_id))

    if loan is None:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    return loan


class LoanCreate(BaseModel):
    artifact_id: UUID
    institution_id: UUID
    loan_date: date
    expected_return_date: date
    notes: str | None = None
    status: str = Field(
        default="Pending",
        pattern="^(Pending|Active)$"
    )


@router.post("/", status_code=201)
def add_loan(loan: LoanCreate):
    """Register a new museum loan."""
    if loan.expected_return_date <= loan.loan_date:
        raise HTTPException(
            status_code=400,
            detail="Expected return date must be after loan date"
        )

    return create_loan(
        loan.model_dump(mode="json", exclude_none=True)
    )
