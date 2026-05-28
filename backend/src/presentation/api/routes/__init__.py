from fastapi import APIRouter

from src.presentation.api.routes import (
    auth,
    clients,
    companies,
    documents,
    exports,
    notifications,
    pdfs,
    quotations,
    shipments,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(quotations.router, prefix="/quotations", tags=["quotations"])
api_router.include_router(shipments.router, prefix="/shipments", tags=["shipments"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
api_router.include_router(pdfs.router, prefix="/pdf", tags=["pdf"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
