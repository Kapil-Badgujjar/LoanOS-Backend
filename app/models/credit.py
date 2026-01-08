from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class CreditResult(Base):
    __tablename__ = "credit_results"

    id = Column(Integer, primary_key=True, index=True)

    application_id = Column(Integer, ForeignKey("loan_applications.id"), unique=True)

    credit_score = Column(Integer)
    active_loans = Column(Integer)
    status = Column(String)  # APPROVED / REJECTED
    reason = Column(String, nullable=True)

    application = relationship("LoanApplication", back_populates="credit_result")
