from pydantic import BaseModel, Field

class ArtistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    birth_year: int | None = None
    death_year: int | None = None
    nationality: str | None = None
    biography: str | None = None

class ArtistUpdate(ArtistCreate):
    pass
