import random
from app.models.kyc import KYCResult
from app.core.enums import ApplicationStatus


class KYCService:
    """Abstract service interface"""
    def run_kyc(self, application):
        raise NotImplementedError

class MockKYCService(KYCService):
    def run_kyc(self, application, db):

        # rule-based or randomized score
        score = random.randint(60, 100)

        status = "PASSED" if score >= 80 else "FAILED"

        result = KYCResult(
            application_id=application.id,
            name_match_score=score,
            status=status,
            reason=None if status == "PASSED" else "Name match score below threshold"
        )

        db.add(result)

        # update workflow status
        if status == "PASSED":
            application.status = ApplicationStatus.KYC_COMPLETED
        else:
            application.status = ApplicationStatus.NOT_ELIGIBLE

        db.commit()
        db.refresh(result)

        return result
