from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.enums import KycDocumentType, KycStatus
from app.models.kyc_document import KycDocument
from app.models.customer_profile import CustomerProfile
from app.models.user import User
from app.schemas.kyc import KycDocumentResponse
from app.utils.file_storage import save_upload

router = APIRouter(prefix="/kyc", tags=["KYC"])


@router.get("/documents", response_model=list[KycDocumentResponse])
def list_documents(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    return (
        db.query(KycDocument)
        .filter(KycDocument.user_id == current_user.id)
        .order_by(KycDocument.created_at.desc())
        .all()
    )


@router.post("/upload", response_model=KycDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    document_type: Annotated[str, Form()],
    file: UploadFile = File(...),
):
    try:
        doc_type = KycDocumentType(document_type)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document type")

    file_path, original_filename = await save_upload(file, f"kyc/{current_user.id}")

    doc = KycDocument(
        user_id=current_user.id,
        document_type=doc_type,
        file_path=file_path,
        original_filename=original_filename,
        status=KycStatus.PENDING,
    )
    db.add(doc)

    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
    if profile and profile.kyc_status in (KycStatus.NOT_SUBMITTED, KycStatus.REJECTED):
        profile.kyc_status = KycStatus.PENDING
    elif profile and profile.kyc_status != KycStatus.APPROVED:
        user_docs = db.query(KycDocument).filter(KycDocument.user_id == current_user.id).all()
        uploaded_types = {d.document_type for d in user_docs}
        uploaded_types.add(doc_type)
        required = {KycDocumentType.ID_PASSPORT, KycDocumentType.PROOF_OF_ADDRESS, KycDocumentType.SELFIE}
        if required.issubset(uploaded_types):
            profile.kyc_status = KycStatus.PENDING

    db.commit()
    db.refresh(doc)
    return doc
