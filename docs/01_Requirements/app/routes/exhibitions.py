from datetime import date
from pydantic import BaseModel, Field
from app.services.exhibitions import create_exhibition
from app.services.exhibitions import update_exhibition
from app.services.exhibitions import assign_artifact_to_exhibition
from app.services.exhibitions import delete_exhibition
from uuid import UUID
from app.services.exhibitions import remove_artifact_from_exhibition
from app.services.exhibitions import get_exhibition_artifacts
from fastapi import APIRouter, HTTPException
from app.services.exhibitions import (
    get_all_exhibitions,
    get_exhibition_by_id,
)

router = APIRouter(
    prefix="/api/exhibitions",
    tags=["Exhibitions"]
)


@router.get("/")
def list_exhibitions():
    """Return all museum exhibitions."""
    return get_all_exhibitions()


@router.get("/{exhibition_id}")
def exhibition_details(exhibition_id: str):
    """Return the details of one exhibition."""
    exhibition = get_exhibition_by_id(exhibition_id)

    if exhibition is None:
        raise HTTPException(
            status_code=404,
            detail="Exhibition not found"
        )

    return exhibition
class ExhibitionCreate(BaseModel):
    exhibition_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    location: str | None = None
    start_date: date
    end_date: date
    status: str = "Planned"


@router.post("/", status_code=201)
def add_exhibition(exhibition: ExhibitionCreate):
    """Create a new museum exhibition."""
    if exhibition.end_date <= exhibition.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    return create_exhibition(
        exhibition.model_dump(mode="json")
    )


@router.put("/{exhibition_id}")
def edit_exhibition(
    exhibition_id: str,
    exhibition: ExhibitionCreate
):
    """Update an existing museum exhibition."""
    if exhibition.end_date <= exhibition.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    updated = update_exhibition(
        exhibition_id,
        exhibition.model_dump(mode="json")
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Exhibition not found"
        )

    return updated

@router.delete("/{exhibition_id}")
def remove_exhibition(exhibition_id: str):
    """Delete an existing museum exhibition."""
    deleted = delete_exhibition(exhibition_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Exhibition not found"
        )

    return {"message": "Exhibition deleted successfully"}




class ArtifactAssignment(BaseModel):
    artifact_id: UUID


@router.post("/{exhibition_id}/artifacts", status_code=201)
def add_artifact_to_exhibition(
    exhibition_id: UUID,
    assignment: ArtifactAssignment
):
    """Assign an artifact to an exhibition."""
    return assign_artifact_to_exhibition(
        str(exhibition_id),
        str(assignment.artifact_id)
    )

@router.get("/{exhibition_id}/artifacts")
def list_exhibition_artifacts(exhibition_id: UUID):
    """List artifacts assigned to an exhibition."""
    return get_exhibition_artifacts(str(exhibition_id))

@router.delete("/{exhibition_id}/artifacts/{artifact_id}")
def unassign_artifact(
    exhibition_id: UUID,
    artifact_id: UUID
):
    """Remove an artifact from an exhibition."""
    removed = remove_artifact_from_exhibition(
        str(exhibition_id),
        str(artifact_id)
    )

    if not removed:
        raise HTTPException(
            status_code=404,
            detail="Artifact assignment not found"
        )

    return {
        "message": "Artifact removed from exhibition successfully"
    }
