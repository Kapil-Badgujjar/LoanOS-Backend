from fastapi import HTTPException
from app.core.enums import ApplicationStatus


allowed_transitions = {
    ApplicationStatus.DRAFT: [ApplicationStatus.KYC_PENDING],
    ApplicationStatus.KYC_PENDING: [ApplicationStatus.KYC_COMPLETED],
    ApplicationStatus.KYC_COMPLETED: [ApplicationStatus.CREDIT_CHECK_PENDING],
    ApplicationStatus.CREDIT_CHECK_PENDING: [ApplicationStatus.CREDIT_CHECK_COMPLETED],
    ApplicationStatus.CREDIT_CHECK_COMPLETED: [
        ApplicationStatus.ELIGIBLE,
        ApplicationStatus.NOT_ELIGIBLE,
    ],
}


def ensure_transition(current, target):
    if target not in allowed_transitions.get(current, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid workflow transition: {current} → {target}",
        )
