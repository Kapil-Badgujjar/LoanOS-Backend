from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class KYCResult(Base):
    __tablename__ = "kyc_results"

    id = Column(Integer, primary_key=True, index=True)

    application_id = Column(Integer, ForeignKey("loan_applications.id"), unique=True)

    name_match_score = Column(Float)
    status = Column(String)   # PASSED / FAILED
    reason = Column(String, nullable=True)

    application = relationship("LoanApplication", back_populates="kyc_result")
