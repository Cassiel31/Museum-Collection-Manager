from app.database import supabase

def get_all_artifacts(search=None, category_id=None, condition=None):
    q = supabase.table("artifacts").select("*, artists(name), categories(category_name)").order("created_at", desc=True)
    if search:
        q = q.ilike("title", f"%{search}%")
    if category_id:
        q = q.eq("category_id", category_id)
    if condition:
        q = q.eq("current_condition", condition)
    return q.execute().data or []

def get_artifact_by_id(artifact_id):
    result = supabase.table("artifacts").select("*, artists(name), categories(category_name)").eq("artifact_id", artifact_id).execute()
    return result.data[0] if result.data else None
