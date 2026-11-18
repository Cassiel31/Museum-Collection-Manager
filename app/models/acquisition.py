from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field

class AcquisitionCreate(BaseModel):
    artifact_id: str
    acquisition_type: str = Field(min_length=1)
    acquisition_date: date
    source_name: str | None = None
    purchase_price: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None

class AcquisitionUpdate(AcquisitionCreate):
    pass
