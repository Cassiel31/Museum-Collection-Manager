from datetime import date
from pydantic import BaseModel, Field
from app.services.exhibitions import create_exhibition
from app.services.exhibitions import update_exhibition
from app.services.exhibitions import delete_exhibition
from fastapi import APIRouter, HTTPException
from app.services.exhibitions import (
    get_all_exhibitions,
    get_exhibition_by_id,
)

router = APIRouter(
    prefix="/api/exhibitions",
    tags=["Exhibitions"]
)


@router.get("/")
def list_exhibitions():
    """Return all museum exhibitions."""
    return get_all_exhibitions()


@router.get("/{exhibition_id}")
def exhibition_details(exhibition_id: str):
    """Return the details of one exhibition."""
    exhibition = get_exhibition_by_id(exhibition_id)

    if exhibition is None:
        raise HTTPException(
            status_code=404,
            detail="Exhibition not found"
        )

    return exhibition
class ExhibitionCreate(BaseModel):
    exhibition_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    location: str | None = None
    start_date: date
    end_date: date
    status: str = "Planned"


@router.post("/", status_code=201)
def add_exhibition(exhibition: ExhibitionCreate):
    """Create a new museum exhibition."""
    if exhibition.end_date <= exhibition.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    return create_exhibition(
        exhibition.model_dump(mode="json")
    )


@router.put("/{exhibition_id}")
def edit_exhibition(
    exhibition_id: str,
    exhibition: ExhibitionCreate
):
    """Update an existing museum exhibition."""
    if exhibition.end_date <= exhibition.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    updated = update_exhibition(
        exhibition_id,
        exhibition.model_dump(mode="json")
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Exhibition not found"
        )

    return updated

@router.delete("/{exhibition_id}")
def remove_exhibition(exhibition_id: str):
    """Delete an existing museum exhibition."""
    deleted = delete_exhibition(exhibition_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Exhibition not found"
        )

    return {"message": "Exhibition deleted successfully"}
