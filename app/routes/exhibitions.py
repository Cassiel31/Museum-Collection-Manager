
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
