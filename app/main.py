from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="The Archive - Museum Collection Manager")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/health")
def health_check():
    return {"status": "The Archive is running!"}

# HTML page routers
from app.routes.pages import router as pages_router
from app.routes.artifacts import router as artifacts_router
from app.routes.management import router as management_router
from app.routes.met_import import router as met_import_router
from app.routes.exhibitions import router as exhibitions_router, api_router as exhibitions_api_router
from app.routes.loans import router as loans_router
from app.routes.institutions import router as institutions_router
from app.routes.availability import router as availability_router
from app.routes.conservation_pages import router as conservation_pages_router

# JSON/API routers retained for conservation modules
from app.routes.staff import router as staff_api_router
from app.routes.restoration import router as restoration_api_router
from app.routes.condition import router as condition_api_router

for route in (pages_router, artifacts_router, management_router, met_import_router,
              exhibitions_router, loans_router, institutions_router, availability_router,
              conservation_pages_router, exhibitions_api_router, staff_api_router,
              restoration_api_router, condition_api_router):
    app.include_router(route)
