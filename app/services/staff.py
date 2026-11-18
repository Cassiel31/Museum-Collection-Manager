
from app.database import supabase
from app.models.staff import StaffCreate, StaffUpdate

TABLE = "staff"


def get_all_staff():
    """Retrieve all staff members."""
    response = (
        supabase.table(TABLE)
        .select("*")
        .order("full_name")
        .execute()
    )
    return response.data


def get_staff_by_id(staff_id: str):
    """Retrieve one staff member by ID."""
    response = (
        supabase.table(TABLE)
        .select("*")
        .eq("staff_id", staff_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def create_staff(staff: StaffCreate):
    """Add a new staff member."""
    data = staff.model_dump(mode="json", exclude_none=True)

    response = (
        supabase.table(TABLE)
        .insert(data)
        .execute()
    )
    return response.data[0] if response.data else None


def update_staff(staff_id: str, staff: StaffUpdate):
    """Update an existing staff member."""
    data = staff.model_dump(mode="json", exclude_unset=True)

    if not data:
        return get_staff_by_id(staff_id)

    response = (
        supabase.table(TABLE)
        .update(data)
        .eq("staff_id", staff_id)
        .execute()
    )
    return response.data[0] if response.data else None


def delete_staff(staff_id: str):
    """Delete a staff member."""
    response = (
        supabase.table(TABLE)
        .delete()
        .eq("staff_id", staff_id)
        .select("staff_id")
        .execute()
    )
    return bool(response.data)
