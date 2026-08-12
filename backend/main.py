import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database.database import init_db
from backend.api.system import router as system_router
from backend.api.diagnosis import router as diagnosis_router
from backend.api.repairs import router as repairs_router
from backend.api.history import router as history_router
from backend.api.settings import router as settings_router
from backend.api.demo import router as demo_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("smartfix.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SmartFix AI Database and Startup Check...")
    await init_db()
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} Backend started on {settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
    yield
    logger.info("SmartFix AI Backend shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SmartFix AI — Intelligent Windows Error Diagnosis and Troubleshooting System",
    lifespan=lifespan
)

# Enable CORS for local Desktop UI and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(system_router)
app.include_router(diagnosis_router)
app.include_router(repairs_router)
app.include_router(history_router)
app.include_router(settings_router)
app.include_router(demo_router)

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "endpoints": {
            "health": "/api/system/health",
            "diagnose": "/api/diagnosis/diagnose",
            "repairs": "/api/repairs",
            "history": "/api/history",
            "settings": "/api/settings",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
