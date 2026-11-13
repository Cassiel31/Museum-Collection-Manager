
from app.database import supabase


def get_all_institutions():
    """Retrieve all institutions from Supabase."""
    response = (
        supabase.table("institutions")
        .select("*")
        .order("institution_name")
        .execute()
    )
    return response.data


def get_institution_by_id(institution_id: str):
    """Retrieve an institution by its UUID."""
    response = (
        supabase.table("institutions")
        .select("*")
        .eq("institution_id", institution_id)
        .execute()
    )
    return response.data[0] if response.data else None
