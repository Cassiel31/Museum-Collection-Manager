from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.database import supabase

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

@router.get("/")
async def dashboard(request: Request):
    def count(table):
        try:
            result = supabase.table(table).select("*", count="exact").execute()
            return result.count if result.count is not None else len(result.data or [])
        except Exception:
            return 0
    try:
        featured = supabase.table("collections").select("*").eq("is_featured", True).order("created_at", desc=True).execute().data or []
        starred = supabase.table("collections").select("*").eq("is_starred", True).order("created_at", desc=True).execute().data or []
        recent = supabase.table("artifacts").select("*").order("created_at", desc=True).limit(5).execute().data or []
        for collection in featured:
            links = supabase.table("collection_artifacts").select("artifact_id").eq("collection_id", collection["collection_id"]).execute().data or []
            ids = [link["artifact_id"] for link in links]
            collection["artifact_count"] = len(ids)
            sample = supabase.table("artifacts").select("image_url").in_("artifact_id", ids).not_.is_("image_url", "null").limit(1).execute().data if ids else []
            collection["cover_image"] = sample[0].get("image_url") if sample else None
    except Exception:
        featured, starred, recent = [], [], []
    context = {"artifact_count":count("artifacts"),"artist_count":count("artists"),
               "category_count":count("categories"),"collection_count":count("collections"),
               "acquisition_count":count("acquisitions"),"exhibition_count":count("exhibitions"),
               "loan_count":count("loans"),"featured_collections":featured,
               "starred_collections":starred,"recent_artifacts":recent}
    return templates.TemplateResponse(request=request,name="dashboard.html",context=context)
