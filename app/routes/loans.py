
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.services.loans import (
    get_all_loans,
    get_loan_by_id,
)

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

