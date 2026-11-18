from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, model_validator

ExhibitionStatus = Literal['Planned','Ongoing','Completed','Cancelled']
class ExhibitionCreate(BaseModel):
    exhibition_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    location: str | None = None
    start_date: date
    end_date: date
    status: ExhibitionStatus = 'Planned'
    @model_validator(mode='after')
    def valid_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError('End date must be after start date')
        return self

class ExhibitionUpdate(ExhibitionCreate):
    pass
