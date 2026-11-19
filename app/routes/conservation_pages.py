
import traceback
from datetime import date
from decimal import Decimal
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import supabase
from app.models.condition_history import ConditionHistoryCreate, ConditionHistoryUpdate
from app.models.restoration import RestorationCreate, RestorationUpdate
from app.models.staff import StaffCreate, StaffUpdate
from app.services.condition import (
    create_condition_history,
    delete_condition_history,
    get_all_condition_history,
    update_condition_history,
)
from app.services.restoration import (
    create_restoration,
    delete_restoration,
    get_all_restorations,
    update_restoration,
)
from app.services.staff import (
    create_staff,
    delete_staff,
    get_all_staff,
    update_staff,
)

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

CONDITIONS = [
    "Excellent", "Good", "Fair", "Poor",
    "Damaged", "Under Restoration", "Restored"
]
STAFF_ROLES = [
    "Curator", "Conservator", "Collection Manager", "Researcher"
]
RESTORATION_STATUSES = [
    "Pending", "In Progress", "Completed", "Cancelled"
]


def _rows(table, columns="*"):
    response = supabase.table(table).select(columns).execute()
    return response.data or []


def _redirect(path: str, message: str, kind: str = "success"):
    return RedirectResponse(
        f"{path}?{kind}={quote(message)}",
        status_code=303
    )


def _page_context(request: Request, **values):
    return {
        "request": request,
        "message": request.query_params.get("message")
        or request.query_params.get("success"),
        "error": request.query_params.get("error"),
        **values,
    }


def _reference_data():
    artifacts = _rows(
        "artifacts", "artifact_id, title, current_condition"
    )
    staff = get_all_staff()

    artifact_names = {
        row["artifact_id"]: row.get("title", row["artifact_id"])
        for row in artifacts
    }
    staff_names = {
        row["staff_id"]: row.get("full_name", row["staff_id"])
        for row in staff
    }

    return artifacts, staff, artifact_names, staff_names


# =========================
# CONSERVATION OVERVIEW
# =========================

@router.get("/conservation")
def conservation_overview(request: Request):
    restorations = get_all_restorations()
    staff = get_all_staff()
    history = get_all_condition_history()
    artifacts = _rows(
        "artifacts", "artifact_id, title, current_condition"
    )

    requiring = sum(
        1 for item in artifacts
        if item.get("current_condition") in ["Poor", "Damaged"]
    )

    context = _page_context(
        request,
        restorations=restorations[:8],
        staff=staff,
        history=history[:8],
        total_staff=len(staff),
        ongoing=sum(
            1 for item in restorations
            if item.get("status") == "In Progress"
        ),
        completed=sum(
            1 for item in restorations
            if item.get("status") == "Completed"
        ),
        requiring_restoration=requiring,
        damaged=sum(
            1 for item in artifacts
            if item.get("current_condition") == "Damaged"
        ),
    )

    return templates.TemplateResponse(
        request=request,
        name="conservation/overview.html",
        context=context
    )


# =========================
# RESTORATION MANAGEMENT
# =========================

@router.get("/conservation/restorations")
def restoration_page(request: Request):
    restorations = get_all_restorations()
    artifacts, staff, artifact_names, staff_names = _reference_data()

    for record in restorations:
        record["artifact_title"] = artifact_names.get(
            record.get("artifact_id"), "Unknown artifact"
        )
        record["staff_name"] = staff_names.get(
            record.get("staff_id"), "Unassigned"
        )

    context = _page_context(
        request,
        restorations=restorations,
        artifacts=artifacts,
        staff=staff,
        active_staff=[
            member for member in staff
            if member.get("employment_status", "Active") == "Active"
        ],
        statuses=RESTORATION_STATUSES
    )

    return templates.TemplateResponse(
        request=request,
        name="conservation/restoration.html",
        context=context
    )


@router.post("/conservation/restorations/create")
def create_restoration_page(
    artifact_id: str = Form(...),
    staff_id: str = Form(...),
    damage_description: str = Form(...),
    restoration_start_date: date = Form(...),
    expected_completion_date: date | None = Form(None),
    actual_completion_date: date | None = Form(None),
    restoration_cost: Decimal | None = Form(None),
    status: str = Form("Pending"),
    notes: str | None = Form(None),
):
    try:
        payload = RestorationCreate(
            artifact_id=artifact_id,
            staff_id=staff_id,
            damage_description=damage_description,
            restoration_start_date=restoration_start_date,
            expected_completion_date=expected_completion_date,
            actual_completion_date=actual_completion_date,
            restoration_cost=restoration_cost,
            status=status,
            notes=notes or None,
        )

        create_restoration(payload)

        return _redirect(
            "/conservation/restorations",
            "Restoration record created."
        )

    except Exception:
        traceback.print_exc()
        return _redirect(
            "/conservation/restorations",
            "Could not create the restoration record.",
            "error"
        )


@router.post("/conservation/restorations/{restoration_id}/update")
def update_restoration_page(
    restoration_id: str,
    staff_id: str = Form(...),
    damage_description: str = Form(...),
    restoration_start_date: date = Form(...),
    expected_completion_date: date | None = Form(None),
    actual_completion_date: date | None = Form(None),
    restoration_cost: Decimal | None = Form(None),
    status: str = Form(...),
    notes: str | None = Form(None),
):
    try:
        payload = RestorationUpdate(
            staff_id=staff_id,
            damage_description=damage_description,
            restoration_start_date=restoration_start_date,
            expected_completion_date=expected_completion_date,
            actual_completion_date=actual_completion_date,
            restoration_cost=restoration_cost,
            status=status,
            notes=notes or None,
        )

        result = update_restoration(restoration_id, payload)

        if result is None:
            return _redirect(
                "/conservation/restorations",
                "Restoration record not found.",
                "error"
            )

        return _redirect(
            "/conservation/restorations",
            "Restoration record updated."
        )

    except Exception:
        traceback.print_exc()
        return _redirect(
            "/conservation/restorations",
            "Could not update the restoration record.",
            "error"
        )


@router.post("/conservation/restorations/{restoration_id}/delete")
def delete_restoration_page(restoration_id: str):
    try:
        if not delete_restoration(restoration_id):
            return _redirect(
                "/conservation/restorations",
                "Restoration record not found.",
                "error"
            )

        return _redirect(
            "/conservation/restorations",
            "Restoration record deleted."
        )

    except Exception:
        traceback.print_exc()
        return _redirect(
            "/conservation/restorations",
            "This record could not be deleted. Check whether it is linked to condition history.",
            "error"
        )


# =========================
# STAFF MANAGEMENT
# =========================

@router.get("/conservation/staff")
def staff_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="conservation/staff.html",
        context=_page_context(
            request,
            staff=get_all_staff(),
            roles=STAFF_ROLES
        ),
    )


@router.post("/conservation/staff/create")
def create_staff_page(
    full_name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    phone: str | None = Form(None),
    date_joined: date | None = Form(None),
    employment_status: str = Form("Active"),
):
    try:
        staff_data = StaffCreate(
            full_name=full_name,
            email=email,
            role=role,
            phone=phone or None,
            date_joined=date_joined,
            employment_status=employment_status,
        )

        create_staff(staff_data)

        return _redirect(
            "/conservation/staff",
            "Staff member added."
        )

    except Exception:
        traceback.print_exc()

        return _redirect(
            "/conservation/staff",
            "Could not add this staff member. Check the terminal for details.",
            "error"
        )


@router.post("/conservation/staff/{staff_id}/update")
def update_staff_page(
    staff_id: str,
    full_name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    phone: str | None = Form(None),
    date_joined: date | None = Form(None),
    employment_status: str = Form("Active"),
):
    try:
        result = update_staff(
            staff_id,
            StaffUpdate(
                full_name=full_name,
                email=email,
                role=role,
                phone=phone or None,
                date_joined=date_joined,
                employment_status=employment_status,
            )
        )

        if result is None:
            return _redirect(
                "/conservation/staff",
                "Staff member not found.",
                "error"
            )

        return _redirect(
            "/conservation/staff",
            "Staff member updated."
        )

    except Exception:
        traceback.print_exc()
        return _redirect(
            "/conservation/staff",
            "Could not update this staff member. Check the email and required fields.",
            "error"
        )


@router.post("/conservation/staff/{staff_id}/delete")
def delete_staff_page(staff_id: str):
    try:
        if not delete_staff(staff_id):
            return _redirect(
                "/conservation/staff",
                "Staff member not found.",
                "error"
            )

        return _redirect(
            "/conservation/staff",
            "Staff member deleted."
        )

    except Exception:
        traceback.print_exc()
        return _redirect(
            "/conservation/staff",
            "This staff member cannot be deleted while restoration records reference them.",
            "error"
        )


# =========================
# CONDITION HISTORY
# =========================

@router.get("/conservation/condition-history")
def condition_history_page(request: Request):
    history = get_all_condition_history()
    artifacts, _, artifact_names, _ = _reference_data()

    for record in history:
        record["artifact_title"] = artifact_names.get(
            record.get("artifact_id"), "Unknown artifact"
        )

    return templates.TemplateResponse(
        request=request,
        name="conservation/condition_history.html",
        context=_page_context(
            request,
            history=history,
            artifacts=artifacts,
            conditions=CONDITIONS
        ),
    )


@router.post("/conservation/condition-history/create")
def create_condition_history_page(
    artifact_id: str = Form(...),
    previous_condition: str = Form(...),
    new_condition: str = Form(...),
    recorded_date: date = Form(...),
    restoration_id: str | None = Form(None),
    remarks: str | None = Form(None),
):
    try:
        create_condition_history(
            ConditionHistoryCreate(
                artifact_id=artifact_id,
                restoration_id=restoration_id or None,
                previous_condition=previous_condition,
                new_condition=new_condition,
                recorded_date=recorded_date,
                remarks=remarks or None,
            )
        )

        # Keep the artifact's current condition aligned with
        # the latest manual inspection.
        supabase.table("artifacts").update(
            {"current_condition": new_condition}
        ).eq("artifact_id", artifact_id).execute()

        return _redirect(
            "/conservation/condition-history",
            "Condition history record added."
        )

    except Exception:
        traceback.print_exc()
        return _redirect(
            "/conservation/condition-history",
            "Could not add the condition record. Check the selected artifact and conditions.",
            "error"
        )


@router.post("/conservation/condition-history/{record_id}/update")
def update_condition_history_page(
    record_id: str,
    previous_condition: str = Form(...),
    new_condition: str = Form(...),
    recorded_date: date = Form(...),
    remarks: str | None = Form(None),
):
    try:
        result = update_condition_history(
            record_id,
            ConditionHistoryUpdate(
                previous_condition=previous_condition,
                new_condition=new_condition,
                recorded_date=recorded_date,
                remarks=remarks or None,
            )
        )

        if result is None:
            return _redirect(
                "/conservation/condition-history",
                "Condition history record not found.",
                "error"
            )

        return _redirect(
            "/conservation/condition-history",
            "Condition history record updated."
        )

    except Exception:
        traceback.print_exc()
        return _redirect(
            "/conservation/condition-history",
            "Could not update this condition record. Check the entered values.",
            "error"
        )


@router.post("/conservation/condition-history/{record_id}/delete")
def delete_condition_history_page(record_id: str):
    try:
        if not delete_condition_history(record_id):
            return _redirect(
                "/conservation/condition-history",
                "Condition history record not found.",
                "error"
            )

        return _redirect(
            "/conservation/condition-history",
            "Condition history record deleted."
        )

    except Exception:
        traceback.print_exc()
        return _redirect(
            "/conservation/condition-history",
            "Could not delete this condition history record.",
            "error"
        )
