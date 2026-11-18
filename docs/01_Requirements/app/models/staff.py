
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


StaffRole = Literal[
    "Curator",
    "Conservator",
    "Collection Manager",
    "Researcher"
]


class StaffCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: str
    phone: str | None = None
    role: StaffRole
    date_joined: date | None = None


class StaffUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    role: StaffRole | None = None
    date_joined: date | None = None


class StaffRecord(StaffCreate):
    staff_id: str
    created_at: datetime | None = None
