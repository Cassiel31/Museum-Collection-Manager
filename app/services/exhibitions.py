from app.database import supabase


def get_all_exhibitions():
    """Retrieve all exhibitions from Supabase."""
    response = (
        supabase.table("exhibitions")
        .select("*")
        .order("start_date", desc=True)
        .execute()
    )

    return response.data


def get_exhibition_by_id(exhibition_id: str):
    """Retrieve a single exhibition."""
    response = (
        supabase.table("exhibitions")
        .select("*")
        .eq("exhibition_id", exhibition_id)
        .execute()
    )

    return response.data[0] if response.data else None