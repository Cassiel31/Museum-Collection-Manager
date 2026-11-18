from pydantic import BaseModel, Field

class CategoryCreate(BaseModel):
    category_name: str = Field(min_length=1, max_length=255)
    description: str | None = None

class CategoryUpdate(CategoryCreate):
    pass
