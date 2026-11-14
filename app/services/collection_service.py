from app.database import supabase

def all_collections():
    return supabase.table("collections").select("*").order("created_at", desc=True).execute().data or []

def collection_by_id(collection_id):
    result = supabase.table("collections").select("*").eq("collection_id", collection_id).execute()
    return result.data[0] if result.data else None

def collection_artifacts(collection_id):
    links = supabase.table("collection_artifacts").select("artifact_id, added_at").eq("collection_id", collection_id).execute().data or []
    ids = [x["artifact_id"] for x in links]
    if not ids: return []
    return supabase.table("artifacts").select("*").in_("artifact_id", ids).execute().data or []

def add_artifacts(collection_id, artifact_ids):
    for artifact_id in artifact_ids:
        existing = supabase.table("collection_artifacts").select("artifact_id").eq("collection_id", collection_id).eq("artifact_id", artifact_id).execute().data
        if not existing:
            supabase.table("collection_artifacts").insert({"collection_id": collection_id, "artifact_id": artifact_id}).execute()

def remove_artifact(collection_id, artifact_id):
    supabase.table("collection_artifacts").delete().eq("collection_id", collection_id).eq("artifact_id", artifact_id).execute()
