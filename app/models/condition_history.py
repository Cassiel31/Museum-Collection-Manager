
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


ArtifactCondition = Literal[
    "Excellent",
    "Good",
    "Fair",
    "Poor",
    "Damaged",
    "Under Restoration",
    "Restored"
]


class ConditionHistoryCreate(BaseModel):
    artifact_id: str
    restoration_id: str | None = None
    previous_condition: ArtifactCondition
    new_condition: ArtifactCondition
    recorded_date: date
    remarks: str | None = None


class ConditionHistoryUpdate(BaseModel):
    previous_condition: ArtifactCondition | None = None
    new_condition: ArtifactCondition | None = None
    recorded_date: date | None = None
    remarks: str | None = None


class ConditionHistoryRecord(ConditionHistoryCreate):
    condition_history_id: str
