
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


RestorationStatus = Literal[
    "Pending",
    "In Progress",
    "Completed",
    "Cancelled"
]


class RestorationCreate(BaseModel):
    artifact_id: str
    staff_id: str
    damage_description: str = Field(min_length=1)
    restoration_start_date: date
    expected_completion_date: date | None = None
    actual_completion_date: date | None = None
    restoration_cost: Decimal | None = Field(default=None, ge=0)
    status: RestorationStatus = "Pending"
    notes: str | None = None


class RestorationUpdate(BaseModel):
    staff_id: str | None = None
    damage_description: str | None = None
    restoration_start_date: date | None = None
    expected_completion_date: date | None = None
    actual_completion_date: date | None = None
    restoration_cost: Decimal | None = Field(default=None, ge=0)
    status: RestorationStatus | None = None
    notes: str | None = None


class RestorationRecord(RestorationCreate):
    restoration_id: str
    created_at: datetime | None = None
