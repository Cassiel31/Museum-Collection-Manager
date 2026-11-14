
from pathlib import Path

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.artifacts import get_all_artifacts, get_artifact_by_id
from app.database import supabase


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# VIEW ALL ARTIFACTS
@router.get("/artifacts", response_class=HTMLResponse)
async def view_artifacts(request: Request):
    artifacts = get_all_artifacts()

    return templates.TemplateResponse(
        request=request,
        name="collection/artifacts.html",
        context={"artifacts": artifacts}
    )


# SHOW ADD ARTIFACT FORM
@router.get("/artifacts/add", response_class=HTMLResponse)
async def add_artifact_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="collection/artifact_form.html",
        context={}
    )


# SAVE NEW ARTIFACT
@router.post("/artifacts/add")
async def create_artifact(
    title: str = Form(...),
    origin: str = Form(""),
    period: str = Form(""),
    creation_year: int | None = Form(None),
    material: str = Form(""),
    dimensions: str = Form(""),
    image_url: str = Form(""),
    current_condition: str = Form(""),
    description: str = Form("")
):
    artifact_data = {
        "title": title,
        "origin": origin or None,
        "period": period or None,
        "creation_year": creation_year,
        "material": material or None,
        "dimensions": dimensions or None,
        "image_url": image_url or None,
        "current_condition": current_condition or None,
        "description": description or None
    }

    supabase.table("artifacts").insert(artifact_data).execute()

    return RedirectResponse(
        url="/artifacts",
        status_code=303
    )


# VIEW SINGLE ARTIFACT
@router.get("/artifacts/{artifact_id}", response_class=HTMLResponse)
async def artifact_details(request: Request, artifact_id: str):
    artifact = get_artifact_by_id(artifact_id)

    if not artifact:
        return HTMLResponse("Artifact not found.", status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="collection/artifact_details.html",
        context={"artifact": artifact}
    )
