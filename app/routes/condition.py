from fastapi import APIRouter, HTTPException, status

from app.models.condition_history import (
    ConditionHistoryCreate,
    ConditionHistoryUpdate,
)

from app.services.condition import (
    get_all_condition_history,
    get_condition_history_by_id,
    get_artifact_condition_history,
    create_condition_history,
    update_condition_history,
    delete_condition_history,
)

router = APIRouter(
    prefix="/condition-history",
    tags=["Conservation - Condition History"]
)


@router.get("/")
def list_condition_history():
    """Retrieve all condition history records."""
    return get_all_condition_history()


@router.get("/artifact/{artifact_id}")
def list_artifact_condition_history(artifact_id: str):
    """Retrieve condition history for one artifact."""
    return get_artifact_condition_history(artifact_id)


@router.get("/{condition_history_id}")
def read_condition_history(condition_history_id: str):
    """Retrieve one condition history record."""
    record = get_condition_history_by_id(condition_history_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Condition history record not found"
        )

    return record


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_condition_history(record: ConditionHistoryCreate):
    """Create a condition history record."""
    return create_condition_history(record)


@router.put("/{condition_history_id}")
def edit_condition_history(
    condition_history_id: str,
    record: ConditionHistoryUpdate
):
    """Update a condition history record."""
    updated = update_condition_history(condition_history_id, record)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Condition history record not found"
        )

    return updated


@router.delete("/{condition_history_id}")
def remove_condition_history(condition_history_id: str):
    """Delete a condition history record."""
    deleted = delete_condition_history(condition_history_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Condition history record not found"
        )

    return {
        "message": "Condition history record deleted successfully"
    }