from pydantic import BaseModel, Field

class ArtifactCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    origin: str | None = None
    period: str | None = None
    creation_year: int | None = None
    material: str | None = None
    dimensions: str | None = None
    image_url: str | None = None
    current_condition: str = "Good"
    description: str | None = None
    artist_id: str | None = None
    category_id: str | None = None

class ArtifactUpdate(ArtifactCreate):
    pass
