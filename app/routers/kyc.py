from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import LoanApplication
from app.services.workflow import ensure_transition
from app.core.enums import ApplicationStatus
from app.services.kyc_service import MockKYCService
from app.routers.application import ensure_app_owner
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/kyc", tags=["KYC"])

kyc_service = MockKYCService()


@router.post("/{application_id}")
def perform_kyc(application_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if not current_user.is_admin:
        raise HTTPException(status_code=403)

    app_obj = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()

    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    
    ensure_app_owner(app_obj, current_user)

    # allowed only if currently in DRAFT or KYC_PENDING
    ensure_transition(app_obj.status, ApplicationStatus.KYC_PENDING)

    # move to pending first
    app_obj.status = ApplicationStatus.KYC_PENDING
    db.commit()

    result = kyc_service.run_kyc(app_obj, db)

    return {
        "application_id": app_obj.id,
        "kyc_status": result.status,
        "name_match_score": result.name_match_score,
        "application_status": app_obj.status,
    }
