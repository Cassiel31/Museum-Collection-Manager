
from app.database import supabase
from app.models.condition_history import (
    ConditionHistoryCreate,
    ConditionHistoryUpdate,
)

TABLE = "condition_history"


def get_all_condition_history():
    """Retrieve all condition history records."""
    response = (
        supabase.table(TABLE)
        .select("*")
        .order("recorded_date", desc=True)
        .execute()
    )
    return response.data


def get_condition_history_by_id(condition_history_id: str):
    """Retrieve one condition history record."""
    response = (
        supabase.table(TABLE)
        .select("*")
        .eq("condition_history_id", condition_history_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def get_artifact_condition_history(artifact_id: str):
    """Retrieve condition history for a specific artifact."""
    response = (
        supabase.table(TABLE)
        .select("*")
        .eq("artifact_id", artifact_id)
        .order("recorded_date", desc=True)
        .execute()
    )
    return response.data


def create_condition_history(record: ConditionHistoryCreate):
    """Add a condition history record."""
    data = record.model_dump(mode="json", exclude_none=True)

    response = (
        supabase.table(TABLE)
        .insert(data)
        .execute()
    )
    return response.data[0] if response.data else None


def update_condition_history(
    condition_history_id: str,
    record: ConditionHistoryUpdate
):
    """Update a condition history record."""
    data = record.model_dump(mode="json", exclude_unset=True)

    if not data:
        return get_condition_history_by_id(condition_history_id)

    response = (
        supabase.table(TABLE)
        .update(data)
        .eq("condition_history_id", condition_history_id)
        .execute()
    )
    return response.data[0] if response.data else None


def delete_condition_history(condition_history_id: str):
    """Delete a condition history record."""
    response = (
        supabase.table(TABLE)
        .delete()
        .eq("condition_history_id", condition_history_id)
        .select("condition_history_id")
        .execute()
    )
    return bool(response.data)
