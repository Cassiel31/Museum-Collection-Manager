
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.services.institutions import (
    get_all_institutions,
    get_institution_by_id,
)

from pydantic import BaseModel, Field
from app.services.institutions import create_institution
from app.services.institutions import update_institution

router = APIRouter(
    prefix="/api/institutions",
    tags=["Institutions"]
)


@router.get("/")
def list_institutions():
    """Return all registered institutions."""
    return get_all_institutions()


@router.get("/{institution_id}")
def institution_details(institution_id: UUID):
    """Return a single institution."""
    institution = get_institution_by_id(str(institution_id))

    if institution is None:
        raise HTTPException(
            status_code=404,
            detail="Institution not found"
        )

    return institution


class InstitutionCreate(BaseModel):
    institution_name: str = Field(min_length=1, max_length=200)
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None


@router.post("/", status_code=201)
def add_institution(institution: InstitutionCreate):
    """Register a new museum or organisation."""
    return create_institution(
        institution.model_dump(exclude_none=True)
    )


@router.put("/{institution_id}")
def edit_institution(
    institution_id: UUID,
    institution: InstitutionCreate
):
    """Update an existing museum or organisation."""
    updated = update_institution(
        str(institution_id),
        institution.model_dump()
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Institution not found"
        )

    return updated
