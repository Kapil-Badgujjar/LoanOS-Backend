from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.admin_deps import get_admin_user

from app.models.application import LoanApplication
from app.models.kyc import KYCResult
from app.models.credit import CreditResult

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/applications")
def list_applications(
    status: str | None = None,
    eligible: bool | None = None,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    query = db.query(LoanApplication)

    if status:
        query = query.filter(LoanApplication.status == status)

    if eligible is not None:
        if eligible:
            query = query.filter(LoanApplication.status == "ELIGIBLE")
        else:
            query = query.filter(LoanApplication.status == "NOT_ELIGIBLE")

    return query.all()


@router.get("/applications/{application_id}")
def get_full_application(application_id: int,
                         db: Session = Depends(get_db),
                         admin=Depends(get_admin_user)):

    app_obj = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()

    if not app_obj:
        return {"error": "Application not found"}

    kyc = db.query(KYCResult).filter(KYCResult.application_id == application_id).first()
    credit = db.query(CreditResult).filter(CreditResult.application_id == application_id).first()

    return {
        "application": app_obj,
        "kyc_result": kyc,
        "credit_result": credit,
        "current_status": app_obj.status
    }
