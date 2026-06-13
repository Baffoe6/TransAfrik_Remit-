from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.beneficiary import Beneficiary
from app.models.enums import BeneficiaryStatus
from app.models.user import User
from app.schemas.beneficiary import BeneficiaryCreate, BeneficiaryResponse, BeneficiaryUpdate

router = APIRouter(prefix="/beneficiaries", tags=["Beneficiaries"])


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
    beneficiary = Beneficiary(user_id=current_user.id, **data.model_dump())
    db.add(beneficiary)
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

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(beneficiary, field, value)

    if beneficiary.status == BeneficiaryStatus.REJECTED:
        beneficiary.status = BeneficiaryStatus.PENDING

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
