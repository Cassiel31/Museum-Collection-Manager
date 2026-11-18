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
    except Exception:
        featured, starred, recent = [], [], []
    context = {"artifact_count":count("artifacts"),"artist_count":count("artists"),"exhibition_count":count("exhibitions"),
               "loan_count":count("loans"),"featured_collections":featured,"starred_collections":starred,"recent_artifacts":recent}
    return templates.TemplateResponse(request=request,name="dashboard.html",context=context)
