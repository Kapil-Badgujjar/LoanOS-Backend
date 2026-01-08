from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    mobile = Column(String, unique=True)
    password_hash = Column(String)

    is_admin = Column(Boolean, default=False)

    applications = relationship("LoanApplication", back_populates="user")
