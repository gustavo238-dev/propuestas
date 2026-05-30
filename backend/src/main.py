from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.presentation.api.routes import api_router
from src.shared.config.settings import settings


app = FastAPI(
    title="Sistema de Gestion de Importaciones Maritimas",
    version="0.1.0",
    description="API empresarial para automatizacion logistica y documental maritima.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
