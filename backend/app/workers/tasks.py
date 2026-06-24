"""异步任务：长耗时 AI 调用（OCR 抽取、视觉定损、报告生成）走 worker。"""

import asyncio

from app.db.session import SessionLocal
from app.workers.celery_app import celery_app


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="ai.extract_document", bind=True, max_retries=2)
def extract_document(self, doc_id: int) -> dict:
    db = SessionLocal()
    try:
        from app.ai.orchestrator import Orchestrator
        from app.platform.documents.service import DocumentService

        svc = DocumentService(db)
        doc = svc.get(doc_id)
        if doc is None:
            return {"error": "document not found"}
        svc.mark(doc, status="processing")

        ocr = Orchestrator(db).router.pick_ocr()
        image_bytes = svc.get_bytes(doc)
        ocr_result = _run(ocr.recognize(image_bytes, ocr_type=doc.type))

        result = _run(
            Orchestrator(db).invoke(
                "ocr_extract",
                ref_type="document",
                ref_id=doc.id,
                ocr_text=ocr_result.text,
                doc_type=doc.type,
            )
        )
        confidence = result["confidence"]
        svc.mark(
            doc,
            status="review" if confidence < 0.7 else "extracted",
            extracted=result["extracted"],
            confidence=confidence,
            raw_text=ocr_result.text,
        )
        return {"document_id": doc_id, "status": doc.status, "confidence": confidence}
    except Exception as exc:  # noqa: BLE001
        raise self.retry(exc=exc, countdown=10) from None
    finally:
        db.close()


@celery_app.task(name="ai.assess_damage", bind=True, max_retries=1)
def assess_damage(self, case_id: int, image_urls: list[str]) -> dict:
    db = SessionLocal()
    try:
        from app.ai.orchestrator import Orchestrator
        from app.models import ClaimCase

        case = db.get(ClaimCase, case_id)
        if case is None:
            return {"error": "case not found"}
        result = _run(
            Orchestrator(db).invoke(
                "damage_assessment",
                ref_type="claim_case",
                ref_id=case.id,
                image_urls=image_urls,
            )
        )
        return {"case_id": case_id, "estimated": result["assessment"].get("total_estimate")}
    except Exception as exc:  # noqa: BLE001
        raise self.retry(exc=exc, countdown=15) from None
    finally:
        db.close()
