
from app.database import supabase


def get_all_loans():
    """Retrieve all loans with artifact and institution details."""
    response = (
        supabase.table("loans")
        .select("*, artifacts(title), institutions(institution_name)")
        .order("loan_date", desc=True)
        .execute()
    )

    return response.data


def get_loan_by_id(loan_id: str):
    """Retrieve one loan using its UUID."""
    response = (
        supabase.table("loans")
        .select("*, artifacts(title), institutions(institution_name)")
        .eq("loan_id", loan_id)
        .execute()
    )

    return response.data[0] if response.data else None

def create_loan(loan_data: dict):
    """Create a new museum loan in Supabase."""
    response = (
        supabase.table("loans")
        .insert(loan_data)
        .execute()
    )

    return response.data[0]
