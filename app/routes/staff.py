from fastapi import APIRouter, HTTPException, status

from app.models.staff import StaffCreate, StaffUpdate
from app.services.staff import (
    get_all_staff,
    get_staff_by_id,
    create_staff,
    update_staff,
    delete_staff,
)

router = APIRouter(
    prefix="/staff",
    tags=["Staff Management"]
)


@router.get("/")
def list_staff():
    """Retrieve all staff members."""
    return get_all_staff()


@router.get("/{staff_id}")
def read_staff(staff_id: str):
    """Retrieve one staff member."""
    staff = get_staff_by_id(staff_id)

    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )

    return staff


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_staff(staff: StaffCreate):
    """Create a new staff member."""
    return create_staff(staff)


@router.put("/{staff_id}")
def edit_staff(staff_id: str, staff: StaffUpdate):
    """Update an existing staff member."""
    updated_staff = update_staff(staff_id, staff)

    if updated_staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )

    return updated_staff


@router.delete("/{staff_id}")
def remove_staff(staff_id: str):
    """Delete a staff member."""
    deleted = delete_staff(staff_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )

    return {"message": "Staff member deleted successfully"}