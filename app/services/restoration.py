
from app.database import supabase
from app.models.restoration import RestorationCreate, RestorationUpdate

TABLE = "restorations"


def get_all_restorations():
    """Retrieve all restoration records."""
    response = (
        supabase.table(TABLE)
        .select("*")
        .order("restoration_start_date", desc=True)
        .execute()
    )
    return response.data


def get_restoration_by_id(restoration_id: str):
    """Retrieve one restoration record by ID."""
    response = (
        supabase.table(TABLE)
        .select("*")
        .eq("restoration_id", restoration_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def create_restoration(restoration: RestorationCreate):
    """Create a restoration record."""
    data = restoration.model_dump(mode="json", exclude_none=True)

    response = (
        supabase.table(TABLE)
        .insert(data)
        .execute()
    )
    return response.data[0] if response.data else None


def update_restoration(restoration_id: str, restoration: RestorationUpdate):
    """Update an existing restoration record."""
    data = restoration.model_dump(mode="json", exclude_unset=True)

    if not data:
        return get_restoration_by_id(restoration_id)

    response = (
        supabase.table(TABLE)
        .update(data)
        .eq("restoration_id", restoration_id)
        .execute()
    )
    return response.data[0] if response.data else None


def delete_restoration(restoration_id: str):
    """Delete a restoration record."""
    response = (
        supabase.table(TABLE)
        .delete()
        .eq("restoration_id", restoration_id)
        .select("restoration_id")
        .execute()
    )
    return bool(response.data)
