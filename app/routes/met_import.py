
from pathlib import Path

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.met_service import search_artifacts, get_artifact, import_artifact
from app.database import supabase

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/met-import", response_class=HTMLResponse)
async def met_import_page(request: Request, q: str = "", message: str = ""):
    artworks = []
    error = None

    if q.strip():
        try:
            object_ids = search_artifacts(q.strip())[:12]

            for object_id in object_ids:
                artwork = get_artifact(object_id)
                if artwork.get("primaryImageSmall"):
                    artworks.append(artwork)

        except Exception as e:
            error = str(e)

    return templates.TemplateResponse(
        request=request,
        name="met_import.html",
        context={
            "artworks": artworks,
            "query": q,
            "error": error,
            "message": message
        }
    )


@router.post("/met-import/import")
async def import_from_met(object_id: int = Form(...)):
    result = import_artifact(object_id, supabase)

    return RedirectResponse(
        url="/met-import?message=imported",
        status_code=303
    )
