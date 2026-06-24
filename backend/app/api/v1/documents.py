from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.ai.orchestrator import Orchestrator
from app.core.deps import current_user
from app.db.session import get_db
from app.models import Document, User
from app.platform.documents.service import DocumentService
from app.schemas.common import DocumentOut, OCRExtractOut

router = APIRouter(prefix="/documents", tags=["document"])


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("general"),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> DocumentOut:
    data = await file.read()
    if not data:
        raise HTTPException(400, "空文件")
    doc = DocumentService(db).upload(
        data=data,
        doc_type=doc_type,
        file_name=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        uploaded_by=user.id,
    )
    return DocumentOut.model_validate(doc)


@router.post("/{doc_id}/extract", response_model=OCRExtractOut)
async def extract_document(
    doc_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(current_user),
) -> OCRExtractOut:
    svc = DocumentService(db)
    doc = svc.get(doc_id)
    if doc is None:
        raise HTTPException(404, "单证不存在")

    doc = svc.mark(doc, status="processing")
    try:
        image_bytes = svc.get_bytes(doc)
        ocr = Orchestrator(db).router.pick_ocr()
        ocr_result = await ocr.recognize(image_bytes, ocr_type=doc.type)

        result = await Orchestrator(db).invoke(
            "ocr_extract",
            ref_type="document",
            ref_id=doc.id,
            ocr_text=ocr_result.text,
            doc_type=doc.type,
        )
        extracted = result["extracted"]
        confidence = result["confidence"]
        svc.mark(doc, status="extracted", extracted=extracted, confidence=confidence, raw_text=ocr_result.text)
    except Exception:
        svc.mark(doc, status="failed")
        raise

    status_str = "review" if confidence < 0.7 else "done"
    return OCRExtractOut(document_id=doc.id, doc_type=doc.type, extracted=extracted, confidence=confidence, status=status_str)


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)) -> DocumentOut:
    doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(404, "单证不存在")
    return DocumentOut.model_validate(doc)


@router.get("", response_model=list[DocumentOut])
def list_documents(
    doc_type: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(current_user),
) -> list[DocumentOut]:
    q = db.query(Document)
    if doc_type:
        q = q.filter(Document.type == doc_type)
    rows = q.order_by(Document.id.desc()).limit(limit).all()
    return [DocumentOut.model_validate(r) for r in rows]
