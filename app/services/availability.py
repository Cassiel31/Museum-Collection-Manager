"""Availability is derived from artifact records and pending/active loans."""
from app.database import supabase


def get_artifact_availability(search: str = ''):
    artifacts = supabase.table('artifacts').select('*').order('title').execute().data or []
    loans = supabase.table('loans').select('artifact_id,status,expected_return_date,actual_return_date,institutions(institution_name)').execute().data or []
    open_loans = {}
    for loan in loans:
        if loan.get('status') in ('Pending', 'Active'):
            open_loans[loan['artifact_id']] = loan
    result = []
    term = search.strip().lower()
    for artifact in artifacts:
        if term and term not in (artifact.get('title') or '').lower():
            continue
        loan = open_loans.get(artifact.get('artifact_id'))
        result.append({'artifact': artifact, 'available': loan is None, 'loan': loan})
    return result
