from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.staff import get_all_staff
from app.services.restoration import get_all_restorations
from app.services.condition import get_all_condition_history

from app.database import supabase


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@router.get("/conservation")
def conservation_overview(request: Request):
    restorations = get_all_restorations()
    staff = get_all_staff()
    history = get_all_condition_history()

    artifacts_response = (
        supabase.table("artifacts")
        .select("artifact_id, current_condition")
        .execute()
    )

    artifacts = artifacts_response.data or []

    return templates.TemplateResponse(
        request=request,
        name="conservation/overview.html",
        context={
            "restorations": restorations,
            "staff": staff,
            "history": history,
            "total_staff": len(staff),
            "ongoing": sum(
                1 for r in restorations
                if r["status"] == "In Progress"
            ),
            "completed": sum(
                1 for r in restorations
                if r["status"] == "Completed"
            ),
            "requiring_restoration": sum(
                1 for a in artifacts
                if a["current_condition"] in ["Poor", "Damaged"]
            ),
        }
    )


@router.get("/conservation/restorations")
def restoration_page(request: Request):
    restorations = get_all_restorations()

    return templates.TemplateResponse(
        request=request,
        name="conservation/restoration.html",
        context={"restorations": restorations}
    )


@router.get("/conservation/staff")
def staff_page(request: Request):
    staff = get_all_staff()

    return templates.TemplateResponse(
        request=request,
        name="conservation/staff.html",
        context={"staff": staff}
    )


@router.get("/conservation/condition-history")
def condition_history_page(request: Request):
    history = get_all_condition_history()

    return templates.TemplateResponse(
        request=request,
        name="conservation/condition_history.html",
        context={"history": history}
    )