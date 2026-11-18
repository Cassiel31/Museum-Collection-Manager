from pydantic import BaseModel, Field

class InstitutionCreate(BaseModel):
    institution_name: str = Field(min_length=1, max_length=255)
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None

class InstitutionUpdate(InstitutionCreate):
    pass
