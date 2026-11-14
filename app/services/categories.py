from app.database import supabase

TABLE = "categories"
PRIMARY_KEY = "category_id"

def get_all():
    return supabase.table(TABLE).select("*").order("created_at", desc=True).execute().data or []

def get_one(record_id):
    rows = supabase.table(TABLE).select("*").eq(PRIMARY_KEY, record_id).execute().data or []
    return rows[0] if rows else None

def create(data):
    return supabase.table(TABLE).insert(data).execute().data

def update(record_id, data):
    return supabase.table(TABLE).update(data).eq(PRIMARY_KEY, record_id).execute().data

def delete(record_id):
    return supabase.table(TABLE).delete().eq(PRIMARY_KEY, record_id).execute()
