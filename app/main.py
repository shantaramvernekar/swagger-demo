from fastapi import FastAPI

from app.core.config import settings
from app.routers import health
from app.routers import items
from app.routers import files
from app.routers import secure


tags_metadata = [
    {"name": "health", "description": "Service health and diagnostics."},
    {"name": "items", "description": "CRUD operations for items."},
    {"name": "files", "description": "File upload endpoints."},
    {"name": "secure", "description": "API key protected endpoints."},
]


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="A package-structured API demonstrating core Swagger/OpenAPI features via FastAPI.",
    contact={"name": "Your Name", "email": "you@example.com"},
    license_info={"name": "MIT"},
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


app.include_router(health.router)
app.include_router(items.router)
app.include_router(files.router)
app.include_router(secure.router)

