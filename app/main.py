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
app.include_router(met_import_router)
app.include_router(artifacts_router)
app.include_router(management_router)
