from sqlalchemy.orm import Session
from sqlalchemy import select
from src.infrastructure.database.models import DocumentModel

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return list(self.db.scalars(select(DocumentModel).order_by(DocumentModel.created_at.desc())))

    def get_by_id(self, doc_id):
        return self.db.get(DocumentModel, doc_id)

    def save(self, document: DocumentModel):
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document