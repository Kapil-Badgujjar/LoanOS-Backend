import random
from app.models.credit import CreditResult
from app.core.enums import ApplicationStatus


class CreditBureauService:
    def run_credit_check(self, application, db):
        raise NotImplementedError

class MockCibilService(CreditBureauService):

    def run_credit_check(self, application, db):

        # ----- base score -----
        score = 700

        # income based scoring
        if application.monthly_income < 20000:
            score -= 100
        elif application.monthly_income < 40000:
            score -= 50
        elif application.monthly_income > 100000:
            score += 50

        # employment penalty
        if application.employment_type.lower() == "self-employed":
            score -= 40

        # active loans mock rule
        # derive active loans number also rule-based
        if application.loan_amount > 10 * application.monthly_income:
            active_loans = 6
        else:
            active_loans = random.randint(0, 4)

        # clamp range
        score = max(300, min(score, 900))

        # decision rules from assignment
        if score < 650 or active_loans > 5:
            status = "REJECTED"
        else:
            status = "APPROVED"

        result = CreditResult(
            application_id=application.id,
            credit_score=score,
            active_loans=active_loans,
            status=status,
            reason=None if status == "APPROVED" else "CIBIL below threshold or too many active loans"
        )

        db.add(result)

        # update application workflow
        if status == "APPROVED":
            application.status = ApplicationStatus.CREDIT_CHECK_COMPLETED
        else:
            application.status = ApplicationStatus.NOT_ELIGIBLE

        db.commit()
        db.refresh(result)

        return result
