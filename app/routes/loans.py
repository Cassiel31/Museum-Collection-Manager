
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.services.loans import (
    get_all_loans,
    get_loan_by_id,
)

from datetime import date
from pydantic import BaseModel, Field
from app.services.loans import create_loan

from app.services.loans import update_loan
from typing import Literal

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

class LoanUpdate(BaseModel):
    expected_return_date: date | None = None
    actual_return_date: date | None = None
    status: Literal["Pending", "Active", "Returned", "Cancelled"] | None = None
    notes: str | None = None


@router.patch("/{loan_id}")
def edit_loan(loan_id: UUID, loan: LoanUpdate):
    """Update a museum loan."""
    existing = get_loan_by_id(str(loan_id))

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    changes = loan.model_dump(
        mode="json",
        exclude_unset=True
    )

    if not changes:
        raise HTTPException(
            status_code=400,
            detail="No changes provided"
        )

    loan_date = date.fromisoformat(existing["loan_date"])

    expected_return = date.fromisoformat(
        changes.get(
            "expected_return_date",
            existing["expected_return_date"]
        )
    )

    if expected_return <= loan_date:
        raise HTTPException(
            status_code=400,
            detail="Expected return date must be after loan date"
        )

    actual_return = changes.get(
        "actual_return_date",
        existing["actual_return_date"]
    )

    if actual_return is not None:
        actual_return = date.fromisoformat(actual_return)

        if actual_return < loan_date:
            raise HTTPException(
                status_code=400,
                detail="Actual return date cannot be before loan date"
            )

    status = changes.get("status", existing["status"])

    if status == "Returned" and actual_return is None:
        raise HTTPException(
            status_code=400,
            detail="Returned loans must have an actual return date"
        )

    if actual_return is not None and status != "Returned":
        raise HTTPException(
            status_code=400,
            detail="An actual return date requires Returned status"
        )

    updated = update_loan(str(loan_id), changes)

    return updated
