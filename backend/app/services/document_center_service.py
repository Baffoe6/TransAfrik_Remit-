import os
import shutil
from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.document_center import DocumentAuditLog, DocumentRecord
from app.models.enums import DocumentCategory, OperationsAuditCategory
from app.services.operations_audit import log_operations_action
from app.utils.file_storage import ensure_upload_dir


def list_documents(
    db: Session,
    *,
    category: DocumentCategory | None = None,
    active_only: bool = True,
) -> list[DocumentRecord]:
    q = db.query(DocumentRecord).order_by(DocumentRecord.created_at.desc())
    if category:
        q = q.filter(DocumentRecord.category == category)
    if active_only:
        q = q.filter(DocumentRecord.is_active.is_(True))
    return q.all()


def upload_document(
    db: Session,
    *,
    file: UploadFile,
    category: DocumentCategory,
    title: str,
    description: str | None,
    uploaded_by: int,
    expires_at: datetime | None = None,
    tenant_id: int | None = None,
    parent_document_id: int | None = None,
    ip_address: str | None = None,
) -> DocumentRecord:
    settings = get_settings()
    ensure_upload_dir()
    doc_dir = os.path.join(settings.upload_dir, "documents", category.value)
    os.makedirs(doc_dir, exist_ok=True)

    version = 1
    if parent_document_id:
        parent = db.query(DocumentRecord).filter(DocumentRecord.id == parent_document_id).first()
        if parent:
            version = parent.version + 1
            parent.is_active = False

    safe_name = file.filename or "document"
    file_path = os.path.join(doc_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}")
    with open(file_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    record = DocumentRecord(
        category=category,
        title=title,
        description=description,
        file_path=file_path,
        file_name=safe_name,
        version=version,
        parent_document_id=parent_document_id,
        expires_at=expires_at,
        uploaded_by=uploaded_by,
        tenant_id=tenant_id,
    )
    db.add(record)
    db.flush()

    db.add(
        DocumentAuditLog(
            document_id=record.id,
            action="uploaded",
            user_id=uploaded_by,
            ip_address=ip_address,
            details=f"version {version}",
        )
    )
    log_operations_action(
        db,
        category=OperationsAuditCategory.DOCUMENT,
        action="document_uploaded",
        entity_type="document",
        entity_id=record.id,
        user_id=uploaded_by,
        ip_address=ip_address,
        details={"category": category.value, "title": title},
    )
    return record


def get_document(db: Session, document_id: int) -> DocumentRecord | None:
    return db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()


def log_document_download(
    db: Session,
    document: DocumentRecord,
    user_id: int,
    ip_address: str | None = None,
) -> None:
    db.add(
        DocumentAuditLog(
            document_id=document.id,
            action="downloaded",
            user_id=user_id,
            ip_address=ip_address,
        )
    )
    log_operations_action(
        db,
        category=OperationsAuditCategory.DOCUMENT,
        action="document_downloaded",
        entity_type="document",
        entity_id=document.id,
        user_id=user_id,
        ip_address=ip_address,
    )
