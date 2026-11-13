
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="The Archive - Museum Collection Manager")

# Connect static files (CSS and images)
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

# Connect HTML templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/health")
def health_check():
    return {"status": "The Archive is running!"}

from app.routes.pages import router as pages_router

app.include_router(pages_router)