from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import supabase
from app.services.collection_service import (
    all_collections, collection_by_id, collection_artifacts,
    add_artifacts, remove_artifact
)

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

def rows(table, order):
    return supabase.table(table).select("*").order(order).execute().data or []

def find_rows(table, key, value):
    return supabase.table(table).select("*").eq(key, value).execute().data or []

@router.get("/artists", response_class=HTMLResponse)
async def artists_page(request: Request, q: str = ""):
    artists = rows("artists", "name")
    if q.strip():
        term = q.strip().lower()
        artists = [a for a in artists if term in (a.get("name") or "").lower()
                   or term in (a.get("nationality") or "").lower()]
    return templates.TemplateResponse(request=request, name="collection/artists.html",
        context={"artists": artists, "q": q})

@router.get("/artists/add", response_class=HTMLResponse)
async def artist_add_page(request: Request):
    return templates.TemplateResponse(request=request, name="collection/artist_form.html", context={"artist": {}})

@router.post("/artists/add")
async def artist_add(name: str = Form(...), birth_year: str = Form(""), death_year: str = Form(""),
                     nationality: str = Form(""), biography: str = Form("")):
    supabase.table("artists").insert({"name": name.strip(),
        "birth_year": int(birth_year) if birth_year.strip() else None,
        "death_year": int(death_year) if death_year.strip() else None,
        "nationality": nationality or None, "biography": biography or None}).execute()
    return RedirectResponse("/artists", 303)

@router.get("/artists/{artist_id}", response_class=HTMLResponse)
async def artist_detail(request: Request, artist_id: str):
    found = find_rows("artists", "artist_id", artist_id)
    if not found: return HTMLResponse("Artist not found", 404)
    artist = found[0]
    artifacts = supabase.table("artifacts").select("*, categories(category_name)").eq("artist_id", artist_id).order("title").execute().data or []
    return templates.TemplateResponse(request=request, name="collection/artist_details.html",
        context={"artist": artist, "artifacts": artifacts})

@router.get("/artists/{artist_id}/edit", response_class=HTMLResponse)
async def artist_edit_page(request: Request, artist_id: str):
    found = find_rows("artists", "artist_id", artist_id)
    if not found: return HTMLResponse("Artist not found", 404)
    return templates.TemplateResponse(request=request, name="collection/artist_form.html", context={"artist": found[0]})

@router.post("/artists/{artist_id}/edit")
async def artist_edit(artist_id: str, name: str = Form(...), birth_year: str = Form(""),
                      death_year: str = Form(""), nationality: str = Form(""), biography: str = Form("")):
    supabase.table("artists").update({"name": name.strip(),
        "birth_year": int(birth_year) if birth_year.strip() else None,
        "death_year": int(death_year) if death_year.strip() else None,
        "nationality": nationality or None, "biography": biography or None}).eq("artist_id", artist_id).execute()
    return RedirectResponse(f"/artists/{artist_id}", 303)

@router.post("/artists/{artist_id}/delete")
async def artist_delete(artist_id: str):
    # FK constraints intentionally prevent deleting an artist still referenced by artifacts.
    supabase.table("artists").delete().eq("artist_id", artist_id).execute()
    return RedirectResponse("/artists", 303)

@router.get("/categories", response_class=HTMLResponse)
async def categories_page(request: Request, q: str = ""):
    categories = rows("categories", "category_name")
    if q.strip():
        term = q.strip().lower()
        categories = [c for c in categories if term in (c.get("category_name") or "").lower()
                      or term in (c.get("description") or "").lower()]
    return templates.TemplateResponse(request=request, name="collection/categories.html",
        context={"categories": categories, "q": q})

@router.get("/categories/add", response_class=HTMLResponse)
async def category_add_page(request: Request):
    return templates.TemplateResponse(request=request, name="collection/category_form.html", context={"category": {}})

@router.post("/categories/add")
async def category_add(category_name: str = Form(...), description: str = Form("")):
    supabase.table("categories").insert({"category_name": category_name.strip(), "description": description or None}).execute()
    return RedirectResponse("/categories", 303)

@router.get("/categories/{category_id}", response_class=HTMLResponse)
async def category_detail(request: Request, category_id: str):
    found = find_rows("categories", "category_id", category_id)
    if not found: return HTMLResponse("Category not found", 404)
    category = found[0]
    artifacts = supabase.table("artifacts").select("*, artists(name)").eq("category_id", category_id).order("title").execute().data or []
    return templates.TemplateResponse(request=request, name="collection/category_details.html",
        context={"category": category, "artifacts": artifacts})

@router.get("/categories/{category_id}/edit", response_class=HTMLResponse)
async def category_edit_page(request: Request, category_id: str):
    found = find_rows("categories", "category_id", category_id)
    if not found: return HTMLResponse("Category not found", 404)
    return templates.TemplateResponse(request=request, name="collection/category_form.html", context={"category": found[0]})

@router.post("/categories/{category_id}/edit")
async def category_edit(category_id: str, category_name: str = Form(...), description: str = Form("")):
    supabase.table("categories").update({"category_name": category_name.strip(), "description": description or None}).eq("category_id", category_id).execute()
    return RedirectResponse(f"/categories/{category_id}", 303)

@router.post("/categories/{category_id}/delete")
async def category_delete(category_id: str):
    supabase.table("categories").delete().eq("category_id", category_id).execute()
    return RedirectResponse("/categories", 303)

@router.get("/acquisitions", response_class=HTMLResponse)
async def acquisitions_page(request: Request, q: str = ""):
    data = supabase.table("acquisitions").select("*, artifacts(title)").order("acquisition_date", desc=True).execute().data or []
    if q.strip():
        term = q.strip().lower()
        data = [x for x in data if term in (x.get("acquisition_type") or "").lower()
                or term in (x.get("source_name") or "").lower()
                or term in ((x.get("artifacts") or {}).get("title") or "").lower()]
    return templates.TemplateResponse(request=request, name="collection/acquisitions.html",
        context={"acquisitions": data, "artifacts": rows("artifacts", "title"), "q": q})

@router.get("/acquisitions/add", response_class=HTMLResponse)
async def acquisition_add_page(request: Request):
    return templates.TemplateResponse(request=request, name="collection/acquisition_form.html",
        context={"artifacts": rows("artifacts", "title")})

@router.post("/acquisitions/add")
async def acquisition_add(artifact_id: str = Form(...), acquisition_type: str = Form(...),
    acquisition_date: str = Form(...), source_name: str = Form(""),
    purchase_price: str = Form(""), notes: str = Form("")):
    supabase.table("acquisitions").insert({"artifact_id": artifact_id, "acquisition_type": acquisition_type,
        "acquisition_date": acquisition_date, "source_name": source_name or None,
        "purchase_price": float(purchase_price) if purchase_price else None, "notes": notes or None}).execute()
    return RedirectResponse("/acquisitions", 303)

@router.get("/acquisitions/{acquisition_id}/edit", response_class=HTMLResponse)
async def acquisition_edit_page(request: Request, acquisition_id: str):
    found = find_rows("acquisitions", "acquisition_id", acquisition_id)
    if not found: return HTMLResponse("Acquisition not found", 404)
    return templates.TemplateResponse(request=request, name="collection/acquisition_form.html",
        context={"acquisition": found[0], "artifacts": rows("artifacts", "title")})

@router.post("/acquisitions/{acquisition_id}/edit")
async def acquisition_edit(acquisition_id: str, artifact_id: str = Form(...), acquisition_type: str = Form(...),
    acquisition_date: str = Form(...), source_name: str = Form(""), purchase_price: str = Form(""), notes: str = Form("")):
    supabase.table("acquisitions").update({"artifact_id": artifact_id, "acquisition_type": acquisition_type,
        "acquisition_date": acquisition_date, "source_name": source_name or None,
        "purchase_price": float(purchase_price) if purchase_price else None, "notes": notes or None}).eq("acquisition_id", acquisition_id).execute()
    return RedirectResponse("/acquisitions", 303)

@router.post("/acquisitions/{acquisition_id}/delete")
async def acquisition_delete(acquisition_id: str):
    supabase.table("acquisitions").delete().eq("acquisition_id", acquisition_id).execute()
    return RedirectResponse("/acquisitions", 303)

@router.get("/collections", response_class=HTMLResponse)
async def collections_page(request: Request, q: str = ""):
    collections = all_collections()
    for c in collections:
        arts = collection_artifacts(c["collection_id"])
        c["artifact_count"] = len(arts)
        c["cover_image"] = next((a.get("image_url") for a in arts if a.get("image_url")), None)
    if q.strip():
        term = q.strip().lower()
        collections = [c for c in collections if term in (c.get("name") or "").lower()
                       or term in (c.get("description") or "").lower()]
    return templates.TemplateResponse(request=request, name="collections/collections.html",
        context={"collections": collections, "q": q})

@router.get("/collections/add", response_class=HTMLResponse)
async def collection_add_page(request: Request):
    return templates.TemplateResponse(request=request, name="collections/collection_form.html", context={"collection": {}})

@router.post("/collections/add")
async def collection_add(name: str = Form(...), description: str = Form("")):
    supabase.table("collections").insert({"name": name.strip(), "description": description or None}).execute()
    return RedirectResponse("/collections", 303)

@router.get("/collections/{collection_id}", response_class=HTMLResponse)
async def collection_detail_page(request: Request, collection_id: str, q: str = ""):
    c = collection_by_id(collection_id)
    if not c: return HTMLResponse("Collection not found", 404)
    artifacts = collection_artifacts(collection_id)
    if q.strip():
        term = q.strip().lower()
        artifacts = [a for a in artifacts if term in (a.get("title") or "").lower()
                     or term in (a.get("origin") or "").lower()
                     or term in (a.get("material") or "").lower()]
    return templates.TemplateResponse(request=request, name="collections/collection_details.html",
        context={"collection": c, "artifacts": artifacts, "q": q})

@router.get("/collections/{collection_id}/edit", response_class=HTMLResponse)
async def collection_edit_page(request: Request, collection_id: str):
    c = collection_by_id(collection_id)
    if not c: return HTMLResponse("Collection not found", 404)
    return templates.TemplateResponse(request=request, name="collections/collection_form.html", context={"collection": c})

@router.post("/collections/{collection_id}/edit")
async def collection_edit(collection_id: str, name: str = Form(...), description: str = Form("")):
    supabase.table("collections").update({"name": name.strip(), "description": description or None}).eq("collection_id", collection_id).execute()
    return RedirectResponse(f"/collections/{collection_id}", 303)

@router.post("/collections/{collection_id}/delete")
async def collection_delete(collection_id: str):
    supabase.table("collection_artifacts").delete().eq("collection_id", collection_id).execute()
    supabase.table("collections").delete().eq("collection_id", collection_id).execute()
    return RedirectResponse("/collections", 303)

@router.post("/collections/{collection_id}/star")
async def collection_star(collection_id: str):
    c = collection_by_id(collection_id)
    if c:
        new_state = not c["is_starred"]
        supabase.table("collections").update({"is_starred": new_state}).eq("collection_id", collection_id).execute()
    return RedirectResponse("/collections", 303)

@router.post("/collections/{collection_id}/feature")
async def collection_feature(collection_id: str):
    c = collection_by_id(collection_id)
    if c: supabase.table("collections").update({"is_featured": not c["is_featured"]}).eq("collection_id", collection_id).execute()
    return RedirectResponse("/collections", 303)

@router.get("/collections/{collection_id}/add-artifacts", response_class=HTMLResponse)
async def collection_add_artifacts_page(request: Request, collection_id: str, q: str = ""):
    c = collection_by_id(collection_id)
    if not c: return HTMLResponse("Collection not found", 404)
    artifacts = rows("artifacts", "title")
    linked = {a["artifact_id"] for a in collection_artifacts(collection_id)}
    available = [a for a in artifacts if a["artifact_id"] not in linked]
    if q.strip():
        term = q.strip().lower()
        available = [a for a in available if term in (a.get("title") or "").lower()
                     or term in (a.get("origin") or "").lower()]
    return templates.TemplateResponse(request=request, name="collections/add_artifacts.html",
        context={"collection": c, "artifacts": available, "q": q})

@router.post("/collections/{collection_id}/add-artifacts")
async def collection_add_artifacts(collection_id: str, artifact_ids: list[str] = Form([])):
    add_artifacts(collection_id, artifact_ids)
    return RedirectResponse(f"/collections/{collection_id}", 303)

@router.post("/collections/{collection_id}/remove/{artifact_id}")
async def collection_remove_artifact(collection_id: str, artifact_id: str):
    remove_artifact(collection_id, artifact_id)
    return RedirectResponse(f"/collections/{collection_id}", 303)


@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    def get_rows(table):
        try: return supabase.table(table).select("*").execute().data or []
        except Exception: return []
    artifacts=get_rows("artifacts"); artists=get_rows("artists"); categories=get_rows("categories")
    collections=get_rows("collections"); acquisitions=get_rows("acquisitions"); exhibitions=get_rows("exhibitions")
    loans=get_rows("loans"); restorations=get_rows("restorations")
    category_counts={}
    for a in artifacts:
        key=a.get("category_id") or "Uncategorised"; category_counts[key]=category_counts.get(key,0)+1
    category_names={c.get("category_id"):c.get("category_name") for c in categories}
    category_summary=[{"name":category_names.get(k,"Uncategorised"),"count":v} for k,v in category_counts.items()]
    artist_names={a.get("artist_id"):a.get("name") for a in artists}
    artist_counts={}
    for artifact in artifacts:
        key=artifact.get("artist_id") or "Unknown artist"
        artist_counts[key]=artist_counts.get(key,0)+1
    artist_summary=[{"name":artist_names.get(k,"Unknown artist"),"count":v} for k,v in artist_counts.items()]
    context={"counts":{"artifacts":len(artifacts),"artists":len(artists),"categories":len(categories),"collections":len(collections),"acquisitions":len(acquisitions),"exhibitions":len(exhibitions),"loans":len(loans),"restorations":len(restorations)},"category_summary":category_summary,"artist_summary":artist_summary}
    return templates.TemplateResponse(request=request,name="reports.html",context=context)
