from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="The Archive - Museum Collection Manager")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/health")
def health_check():
    return {"status": "The Archive is running!"}

from app.routes.pages import router as pages_router
from app.routes.met_import import router as met_import_router
from app.routes.artifacts import router as artifacts_router
from app.routes.management import router as management_router

app.include_router(pages_router)

from app.routes.conservation_pages import router as conservation_pages_router
app.include_router(conservation_pages_router)


# Conservation API routers
from app.routes.staff import router as staff_router
from app.routes.restoration import router as restoration_router
from app.routes.condition import router as condition_router




