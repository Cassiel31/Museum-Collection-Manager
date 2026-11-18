"""Database operations for the existing loans table."""
from app.database import supabase

TABLE = 'loans'


def get_all_loans():
    return supabase.table(TABLE).select('*, artifacts(title), institutions(institution_name)').order('loan_date', desc=True).execute().data or []


def get_loan_by_id(loan_id: str):
    rows = supabase.table(TABLE).select('*').eq('loan_id', loan_id).limit(1).execute().data or []
    return rows[0] if rows else None


def artifact_has_open_loan(artifact_id: str, exclude_loan_id: str | None = None):
    query = supabase.table(TABLE).select('loan_id').eq('artifact_id', artifact_id).in_('status', ['Pending', 'Active'])
    rows = query.execute().data or []
    return any(row.get('loan_id') != exclude_loan_id for row in rows)


def create_loan(data: dict):
    rows = supabase.table(TABLE).insert(data).execute().data or []
    return rows[0] if rows else None


def update_loan(loan_id: str, data: dict):
    rows = supabase.table(TABLE).update(data).eq('loan_id', loan_id).execute().data or []
    return rows[0] if rows else None


def delete_loan(loan_id: str):
    rows = supabase.table(TABLE).delete().eq('loan_id', loan_id).select('loan_id').execute().data or []
    return bool(rows)
