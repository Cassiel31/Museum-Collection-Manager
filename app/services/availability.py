
from app.database import supabase


def check_artifact_availability(artifact_id: str):
    """Check whether an artifact is available."""

    artifact_response = (
        supabase.table("artifacts")
        .select("artifact_id, title, current_condition")
        .eq("artifact_id", artifact_id)
        .execute()
    )

    if not artifact_response.data:
        return None

    artifact = artifact_response.data[0]

    loans = (
        supabase.table("loans")
        .select("loan_id")
        .eq("artifact_id", artifact_id)
        .in_("status", ["Pending", "Active"])
        .execute()
    )

    restorations = (
        supabase.table("restorations")
        .select("restoration_id")
        .eq("artifact_id", artifact_id)
        .eq("status", "In Progress")
        .execute()
    )

    exhibitions = (
        supabase.table("exhibition_artifacts")
        .select("exhibition_id, exhibitions(start_date, end_date, status)")
        .eq("artifact_id", artifact_id)
        .execute()
    )

    from datetime import date

    today = date.today()

    currently_exhibited = any(
        record["exhibitions"] is not None
        and record["exhibitions"]["status"] == "Ongoing"
        and date.fromisoformat(
            record["exhibitions"]["start_date"]
        ) <= today
        <= date.fromisoformat(
            record["exhibitions"]["end_date"]
        )
        for record in exhibitions.data
    )

    reasons = []

    if loans.data:
        reasons.append("Artifact has an active or pending loan")

    if restorations.data:
        reasons.append("Artifact is undergoing restoration")

    if currently_exhibited:
        reasons.append("Artifact is currently exhibited")

    return {
        "artifact_id": artifact_id,
        "title": artifact["title"],
        "available": len(reasons) == 0,
        "reasons": reasons
    }
