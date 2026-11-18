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


def create_exhibition(exhibition_data: dict):
    """Create a new exhibition in Supabase."""
    response = (
        supabase.table("exhibitions")
        .insert(exhibition_data)
        .execute()
    )

    return response.data[0]

def update_exhibition(exhibition_id: str, exhibition_data: dict):
    """Update an existing exhibition in Supabase."""
    response = (
        supabase.table("exhibitions")
        .update(exhibition_data)
        .eq("exhibition_id", exhibition_id)
        .execute()
    )

    return response.data[0] if response.data else None

def delete_exhibition(exhibition_id: str):
    """Delete an exhibition from Supabase."""
    response = (
        supabase.table("exhibitions")
        .delete()
        .eq("exhibition_id", exhibition_id)
        .execute()
    )

    return bool(response.data)

def assign_artifact_to_exhibition(
    exhibition_id: str,
    artifact_id: str
):
    """Assign an artifact to an exhibition."""
    response = (
        supabase.table("exhibition_artifacts")
        .insert({
            "exhibition_id": exhibition_id,
            "artifact_id": artifact_id
        })
        .execute()
    )

    return response.data[0]

def get_exhibition_artifacts(exhibition_id: str):
    """Retrieve artifacts assigned to an exhibition."""
    response = (
        supabase.table("exhibition_artifacts")
        .select("artifact_id, artifacts(*)")
        .eq("exhibition_id", exhibition_id)
        .execute()
    )

    return response.data

def remove_artifact_from_exhibition(
    exhibition_id: str,
    artifact_id: str
):
    """Remove an artifact assignment from an exhibition."""
    response = (
        supabase.table("exhibition_artifacts")
        .delete()
        .eq("exhibition_id", exhibition_id)
        .eq("artifact_id", artifact_id)
        .execute()
    )

    return bool(response.data)
