from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import LoanApplication
from app.core.enums import ApplicationStatus
from app.schemas.application import ApplicationCreate
from app.services.validators import validate_pan, calculate_age

from app.core.deps import get_current_user
from app.models.user import User

from app.models.kyc import KYCResult
from app.models.credit import CreditResult

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_application(
    req: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # PAN format validation
    if not validate_pan(req.pan):
        raise HTTPException(status_code=400, detail="Invalid PAN format")

    # Age validation
    if calculate_age(req.dob) < 21:
        raise HTTPException(status_code=400, detail="Applicant must be at least 21 years old")

    # Loan amount rule
    if req.loan_amount > 20 * req.monthly_income:
        raise HTTPException(
            status_code=400,
            detail="Loan amount cannot exceed 20 times the monthly income",
        )

    application = LoanApplication(
        full_name=req.full_name,
        mobile=req.mobile,
        pan=req.pan,
        dob=req.dob,
        employment_type=req.employment_type,
        monthly_income=req.monthly_income,
        loan_amount=req.loan_amount,
        status=ApplicationStatus.DRAFT,
        user_id=current_user.id,  # temporarily static — later we will decode JWT user
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "message": "Application created",
        "application_id": application.id,
        "status": application.status,
    }

@router.get("/")
def list_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    apps = db.query(LoanApplication).filter(LoanApplication.user_id == current_user.id).all()
    return apps

@router.get("/{application_id}")
def get_full_application(application_id: int,
                         db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    app_obj = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()

    if not app_obj:
        return {"error": "Application not found"}

    ensure_app_owner(app_obj, current_user)
    
    kyc = db.query(KYCResult).filter(KYCResult.application_id == application_id).first()
    credit = db.query(CreditResult).filter(CreditResult.application_id == application_id).first()

    return {
        "application": app_obj,
        "kyc_result": kyc,
        "credit_result": credit,
        "current_status": app_obj.status
    }

def ensure_app_owner(application, user):
    if application.user_id != user.id and not user.is_admin :
        raise HTTPException(status_code=403, detail="Not authorized to access this application")
