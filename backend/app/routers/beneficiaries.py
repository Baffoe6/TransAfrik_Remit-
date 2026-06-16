from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.beneficiary import Beneficiary
from app.models.customer_profile import CustomerProfile
from app.models.enums import BeneficiaryStatus
from app.models.user import User
from app.schemas.beneficiary import BeneficiaryCreate, BeneficiaryResponse, BeneficiaryUpdate
from app.services.beneficiary_compliance import evaluate_beneficiary_compliance, resolve_beneficiary_status

router = APIRouter(prefix="/beneficiaries", tags=["Beneficiaries"])


def _apply_compliance_status(
    db: Session,
    *,
    user: User,
    beneficiary: Beneficiary,
    profile: CustomerProfile | None,
) -> list[dict]:
    flags = evaluate_beneficiary_compliance(db, user=user, beneficiary=beneficiary, profile=profile)
    beneficiary.status = resolve_beneficiary_status(flags)
    if beneficiary.status == BeneficiaryStatus.PENDING:
        beneficiary.rejection_reason = None
    return flags


@router.get("", response_model=list[BeneficiaryResponse])
def list_beneficiaries(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    return (
        db.query(Beneficiary)
        .filter(Beneficiary.user_id == current_user.id, Beneficiary.is_active.is_(True))
        .order_by(Beneficiary.created_at.desc())
        .all()
    )


@router.post("", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiary(
    data: BeneficiaryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
    beneficiary = Beneficiary(user_id=current_user.id, **data.model_dump())
    db.add(beneficiary)
    db.flush()
    _apply_compliance_status(db, user=current_user, beneficiary=beneficiary, profile=profile)
    db.commit()
    db.refresh(beneficiary)
    return beneficiary


@router.get("/{beneficiary_id}", response_model=BeneficiaryResponse)
def get_beneficiary(
    beneficiary_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    beneficiary = (
        db.query(Beneficiary)
        .filter(Beneficiary.id == beneficiary_id, Beneficiary.user_id == current_user.id)
        .first()
    )
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")
    return beneficiary


@router.patch("/{beneficiary_id}", response_model=BeneficiaryResponse)
def update_beneficiary(
    beneficiary_id: int,
    data: BeneficiaryUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    beneficiary = (
        db.query(Beneficiary)
        .filter(Beneficiary.id == beneficiary_id, Beneficiary.user_id == current_user.id)
        .first()
    )
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")

    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(beneficiary, field, value)

    _apply_compliance_status(db, user=current_user, beneficiary=beneficiary, profile=profile)
    db.commit()
    db.refresh(beneficiary)
    return beneficiary


@router.delete("/{beneficiary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_beneficiary(
    beneficiary_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    beneficiary = (
        db.query(Beneficiary)
        .filter(Beneficiary.id == beneficiary_id, Beneficiary.user_id == current_user.id)
        .first()
    )
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")
    beneficiary.is_active = False
    db.commit()
