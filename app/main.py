
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

from app.routes.collections import router as collections_router
app.include_router(collections_router)

from app.routes.conservation_pages import router as conservation_pages_router
app.include_router(conservation_pages_router)


# Conservation API routers
from app.routes.staff import router as staff_router
from app.routes.restoration import router as restoration_router
from app.routes.condition import router as condition_router

app.include_router(staff_router)
app.include_router(restoration_router)
app.include_router(condition_router)