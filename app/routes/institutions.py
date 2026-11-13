
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.services.institutions import (
    get_all_institutions,
    get_institution_by_id,
)

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
v