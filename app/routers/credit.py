from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import LoanApplication
from app.core.enums import ApplicationStatus
from app.services.workflow import ensure_transition
from app.services.credit_service import MockCibilService
from app.routers.application import ensure_app_owner
from app.core.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/credit", tags=["Credit Bureau"])

credit_service = MockCibilService()


@router.post("/{application_id}")
def run_credit_check(application_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if not current_user.is_admin:
        raise HTTPException(status_code=403)
    
    app_obj = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    if app_obj.status != "KYC_COMPLETED":
        raise HTTPException(status_code=400)

    ensure_app_owner(app_obj, current_user)

    # must be KYC completed to proceed
    ensure_transition(app_obj.status, ApplicationStatus.CREDIT_CHECK_PENDING)

    # set pending
    app_obj.status = ApplicationStatus.CREDIT_CHECK_PENDING
    db.commit()

    result = credit_service.run_credit_check(app_obj, db)

    return {
        "application_id": app_obj.id,
        "credit_score": result.credit_score,
        "active_loans": result.active_loans,
        "credit_status": result.status,
        "application_status": app_obj.status
    }
