import time
import uuid

from sqlalchemy.orm import Session

from app.models import Document
from app.platform.documents import storage


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upload(
        self,
        *,
        data: bytes,
        doc_type: str,
        file_name: str | None = None,
        mime_type: str = "application/octet-stream",
        uploaded_by: int | None = None,
        org_id: int | None = None,
        case_id: int | None = None,
    ) -> Document:
        ext = (file_name or "").rsplit(".", 1)[-1] if file_name else "bin"
        object_key = f"docs/{doc_type}/{time.strftime('%Y%m%d')}/{uuid.uuid4().hex}.{ext}"
        storage.put_bytes(object_key, data, content_type=mime_type)
        doc = Document(
            type=doc_type,
            object_key=object_key,
            file_name=file_name,
            mime_type=mime_type,
            size=len(data),
            status="uploaded",
            uploaded_by=uploaded_by,
            org_id=org_id,
            case_id=case_id,
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get(self, doc_id: int) -> Document | None:
        return self.db.get(Document, doc_id)

    def get_bytes(self, doc: Document) -> bytes:
        return storage.get_bytes(doc.object_key)

    def mark(self, doc: Document, *, status: str, extracted: dict | None = None, confidence: float | None = None, raw_text: str | None = None) -> Document:
        doc.status = status
        if extracted is not None:
            doc.extracted = extracted
        if confidence is not None:
            doc.confidence = confidence
        if raw_text is not None:
            doc.raw_text = raw_text
        self.db.commit()
        self.db.refresh(doc)
        return doc
