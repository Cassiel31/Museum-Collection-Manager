
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.services.availability import check_artifact_availability


router = APIRouter(
    prefix="/api/availability",
    tags=["Artifact Availability"]
)


@router.get("/{artifact_id}")
def artifact_availability(artifact_id: UUID):
    """Check an artifact's current availability."""

    result = check_artifact_availability(str(artifact_id))

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Artifact not found"
        )

    return result

