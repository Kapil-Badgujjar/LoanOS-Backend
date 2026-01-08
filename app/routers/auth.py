from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    full_name: str
    mobile: str
    password: str


class LoginRequest(BaseModel):
    mobile: str
    password: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user using JSON body."""
    existing = db.query(User).filter(User.mobile == req.mobile).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    try:
        password_hash = hash_password(req.password)
    except ValueError as e:
        # clear feedback for clients if hashing fails (e.g. password too long for some backends)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    user = User(
        full_name=req.full_name,
        mobile=req.mobile,
        password_hash=password_hash,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    return {"message": "Registered successfully", "user_id": user.id}


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login with JSON body; returns access token."""
    user = db.query(User).filter(User.mobile == req.mobile).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({
        "user_id": user.id,
        "is_admin": user.is_admin,   # ✅ REQUIRED
    })

    return {"access_token": token, "token_type": "bearer"}
