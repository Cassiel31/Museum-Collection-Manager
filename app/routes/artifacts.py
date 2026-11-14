from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import supabase
from app.services.artifacts import get_all_artifacts, get_artifact_by_id

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

@router.get("/artifacts", response_class=HTMLResponse)
async def view_artifacts(request: Request, q: str = "", category_id: str = "", condition: str = ""):
    artifacts = get_all_artifacts(q.strip() or None, category_id or None, condition or None)
    categories = supabase.table("categories").select("*").order("category_name").execute().data or []
    return templates.TemplateResponse(request=request, name="collection/artifacts.html",
        context={"artifacts": artifacts, "categories": categories, "q": q, "selected_category": category_id, "selected_condition": condition})

@router.get("/artifacts/add", response_class=HTMLResponse)
async def add_artifact_page(request: Request):
    context = {"artists": supabase.table("artists").select("*").order("name").execute().data or [],
               "categories": supabase.table("categories").select("*").order("category_name").execute().data or [],
               "artifact": {}}
    return templates.TemplateResponse(request=request, name="collection/artifact_form.html", context=context)

@router.post("/artifacts/add")
async def create_artifact(title: str = Form(...), origin: str = Form(""), period: str = Form(""),
    creation_year: str = Form(""), material: str = Form(""), dimensions: str = Form(""),
    image_url: str = Form(""), current_condition: str = Form("Good"), description: str = Form(""),
    artist_id: str = Form(""), category_id: str = Form("")):
    data = {"title":title.strip(), "origin":origin or None, "period":period or None,
        "creation_year":int(creation_year) if creation_year.strip() else None, "material":material or None,
        "dimensions":dimensions or None, "image_url":image_url or None, "current_condition":current_condition or "Good",
        "description":description or None, "artist_id":artist_id or None, "category_id":category_id or None}
    supabase.table("artifacts").insert(data).execute()
    return RedirectResponse("/artifacts", status_code=303)

@router.get("/artifacts/{artifact_id}/edit", response_class=HTMLResponse)
async def edit_artifact_page(request: Request, artifact_id: str):
    artifact = get_artifact_by_id(artifact_id)
    if not artifact: return HTMLResponse("Artifact not found", status_code=404)
    context = {"artifact":artifact, "artists":supabase.table("artists").select("*").order("name").execute().data or [],
               "categories":supabase.table("categories").select("*").order("category_name").execute().data or []}
    return templates.TemplateResponse(request=request, name="collection/artifact_form.html", context=context)

@router.post("/artifacts/{artifact_id}/edit")
async def edit_artifact(artifact_id: str, title: str = Form(...), origin: str = Form(""), period: str = Form(""),
    creation_year: str = Form(""), material: str = Form(""), dimensions: str = Form(""), image_url: str = Form(""),
    current_condition: str = Form("Good"), description: str = Form(""), artist_id: str = Form(""), category_id: str = Form("")):
    data = {"title":title.strip(), "origin":origin or None, "period":period or None,
        "creation_year":int(creation_year) if creation_year.strip() else None, "material":material or None,
        "dimensions":dimensions or None, "image_url":image_url or None, "current_condition":current_condition,
        "description":description or None, "artist_id":artist_id or None, "category_id":category_id or None}
    supabase.table("artifacts").update(data).eq("artifact_id", artifact_id).execute()
    return RedirectResponse(f"/artifacts/{artifact_id}", status_code=303)

@router.post("/artifacts/{artifact_id}/delete")
async def delete_artifact(artifact_id: str):
    # Preserve linked history: database foreign keys may reject deletion if records depend on this artifact.
    supabase.table("artifacts").delete().eq("artifact_id", artifact_id).execute()
    return RedirectResponse("/artifacts", status_code=303)

@router.get("/artifacts/{artifact_id}", response_class=HTMLResponse)
async def artifact_details(request: Request, artifact_id: str):
    artifact = get_artifact_by_id(artifact_id)
    if not artifact: return HTMLResponse("Artifact not found.", status_code=404)
    return templates.TemplateResponse(request=request, name="collection/artifact_details.html", context={"artifact":artifact})
