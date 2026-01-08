from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import LoanApplication
from app.models.credit import CreditResult
from app.core.enums import ApplicationStatus
from app.services.workflow import ensure_transition
from app.services.eligibility_service import EligibilityService
from app.routers.application import ensure_app_owner
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])

eligibility_service = EligibilityService()


@router.post("/{application_id}")
def run_eligibility(application_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if not current_user.is_admin:
        raise HTTPException(status_code=403)

    app_obj = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()

    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    if app_obj.status != "CREDIT_CHECK_COMPLETED":
        raise HTTPException(
            status_code=400,
            detail="Eligibility can only be evaluated after credit check"
        )
    
    ensure_app_owner(app_obj, current_user)

    # must have credit check completed
    ensure_transition(app_obj.status, ApplicationStatus.ELIGIBLE)

    credit = db.query(CreditResult).filter(CreditResult.application_id == application_id).first()

    if not credit:
        raise HTTPException(status_code=400, detail="Credit result missing")

    result = eligibility_service.evaluate(app_obj, credit, db)

    return {
        "application_id": application_id,
        "application_status": app_obj.status,
        **result
    }
