from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.database.models import DocumentModel


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[DocumentModel]:
        return list(self.db.scalars(select(DocumentModel).order_by(DocumentModel.created_at.desc())))

    def get_by_id(self, document_id: UUID) -> DocumentModel | None:
        return self.db.get(DocumentModel, document_id)

    def save(self, document: DocumentModel) -> DocumentModel:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
