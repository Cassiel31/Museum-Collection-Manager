from fastapi import APIRouter, HTTPException, status

from app.models.restoration import RestorationCreate, RestorationUpdate
from app.services.restoration import (
    get_all_restorations,
    get_restoration_by_id,
    create_restoration,
    update_restoration,
    delete_restoration,
)

router = APIRouter(
    prefix="/restorations",
    tags=["Conservation - Restorations"]
)


@router.get("/")
def list_restorations():
    """Retrieve all restoration records."""
    return get_all_restorations()


@router.get("/{restoration_id}")
def read_restoration(restoration_id: str):
    """Retrieve one restoration record."""
    restoration = get_restoration_by_id(restoration_id)

    if restoration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restoration record not found"
        )

    return restoration


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_restoration(restoration: RestorationCreate):
    """Create a restoration record."""
    return create_restoration(restoration)


@router.put("/{restoration_id}")
def edit_restoration(
    restoration_id: str,
    restoration: RestorationUpdate
):
    """Update a restoration record."""
    updated = update_restoration(restoration_id, restoration)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restoration record not found"
        )

    return updated


@router.delete("/{restoration_id}")
def remove_restoration(restoration_id: str):
    """Delete a restoration record."""
    deleted = delete_restoration(restoration_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restoration record not found"
        )

    return {"message": "Restoration record deleted successfully"}