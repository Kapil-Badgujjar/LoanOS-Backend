from sqlalchemy import Column, Integer, String, Float, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.core.enums import ApplicationStatus
import datetime

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"))

    full_name = Column(String)
    mobile = Column(String)
    pan = Column(String, index=True)
    dob = Column(Date)

    employment_type = Column(String)
    monthly_income = Column(Float)
    loan_amount = Column(Float)

    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.DRAFT)

    created_at = Column(Date, default=datetime.date.today)

    user = relationship("User", back_populates="applications")
    kyc_result = relationship("KYCResult", back_populates="application", uselist=False)
    credit_result = relationship("CreditResult", back_populates="application", uselist=False)


