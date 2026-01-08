import math
from app.core.enums import ApplicationStatus


class EligibilityService:

    def evaluate(self, application, credit_result, db):

        # reject if credit rejected already
        if credit_result.status == "REJECTED":
            application.status = ApplicationStatus.NOT_ELIGIBLE
            db.commit()
            return {
                "eligible": False,
                "reason": "Credit rejected by bureau"
            }

        # monthly interest rate
        r = 0.12 / 12   # 12% annually
        n = 36          # 36 months

        # EMI formula:  P * r * (1+r)^n / ((1+r)^n - 1)
        emi = (
            application.loan_amount
            * r
            * (1 + r) ** n
            / ((1 + r) ** n - 1)
        )

        # income based rule
        if application.employment_type.lower() == "salaried":
            max_emi = 0.5 * application.monthly_income
        else:
            max_emi = 0.4 * application.monthly_income

        if emi > max_emi:
            application.status = ApplicationStatus.NOT_ELIGIBLE
            db.commit()

            return {
                "eligible": False,
                "emi": round(emi, 2),
                "max_allowed_emi": round(max_emi, 2),
                "reason": "EMI exceeds allowed threshold"
            }

        # otherwise eligible
        application.status = ApplicationStatus.ELIGIBLE
        db.commit()

        return {
            "eligible": True,
            "emi": round(emi, 2),
            "max_allowed_emi": round(max_emi, 2),
            "reason": "Eligible as per income and credit rules"
        }
