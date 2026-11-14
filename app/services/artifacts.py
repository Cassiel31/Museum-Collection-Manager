from app.database import supabase


def get_all_artifacts():
    response = (
        supabase.table("artifacts")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []
def get_artifact_by_id(artifact_id):
    response = (
        supabase.table("artifacts")
        .select("*")
        .eq("artifact_id", artifact_id)
        .single()
        .execute()
    )

    return response.data