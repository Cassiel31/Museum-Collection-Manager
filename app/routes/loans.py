
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

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi import Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.services.loans import create_loan
from app.services.institutions import get_all_institutions
from postgrest.exceptions import APIError
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

# HTML page routes
page_router = APIRouter(
    prefix="/loans",
    tags=["Loan Pages"]
)

templates = Jinja2Templates(directory="app/templates")


@page_router.get("/", response_class=HTMLResponse)
def loans_page(request: Request):
    """Display the museum loan listing page."""

    loans = get_all_loans()

    return templates.TemplateResponse(
        request=request,
        name="loans/list.html",
        context={"loans": loans}
    )

@page_router.get("/new", response_class=HTMLResponse)
def new_loan_page(request: Request):
    """Display the new loan registration form."""

    institutions = get_all_institutions()

    return templates.TemplateResponse(
        request=request,
        name="loans/create.html",
        context={"institutions": institutions}
    )


@page_router.post("/new")
def submit_new_loan(
    request: Request,
    artifact_id: UUID = Form(...),
    institution_id: UUID = Form(...),
    loan_date: date = Form(...),
    expected_return_date: date = Form(...),
    status: str = Form("Pending"),
    notes: str = Form("")
):
    """Validate and register a new museum loan."""

    error = None

    if expected_return_date <= loan_date:
        error = "Expected return date must be after loan date."
    elif status not in {"Pending", "Active"}:
        error = "Invalid loan status."

    if error is None:
        loan_data = {
            "artifact_id": str(artifact_id),
            "institution_id": str(institution_id),
            "loan_date": loan_date.isoformat(),
            "expected_return_date": expected_return_date.isoformat(),
            "status": status,
            "notes": notes
        }

        try:
            create_loan(loan_data)
        except APIError as exc:
            if exc.code == "23503":
                error = "Artifact or institution not found."
            elif exc.code in {"23514", "P0001"}:
                error = (
                    "The loan could not be created because "
                    "it violates a museum loan restriction."
                )
            else:
                raise

    if error:
        institutions = get_all_institutions()

        return templates.TemplateResponse(
            request=request,
            name="loans/create.html",
            context={
                "institutions": institutions,
                "error": error
            },
            status_code=400
        )

    return RedirectResponse(
        url="/loans/",
        status_code=303
    )

@page_router.get("/{loan_id}", response_class=HTMLResponse)
def loan_details_page(request: Request, loan_id: UUID):
    """Display the details of an individual loan."""

    loan = get_loan_by_id(str(loan_id))

    if loan is None:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="loans/details.html",
        context={"loan": loan}
    )