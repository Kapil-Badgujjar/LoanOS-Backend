import os
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def seed_admin_user():
    db: Session = SessionLocal()

    admin_mobile = os.getenv("ADMIN_MOBILE")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_name = os.getenv("ADMIN_NAME", "Admin")

    # Safety check
    if not admin_mobile or not admin_password:
        print("Admin seed skipped: env vars not set")
        return

    try:
        admin = db.query(User).filter(User.mobile == admin_mobile).first()

        if admin:
            print("Admin user already exists")
            return

        admin_user = User(
            full_name=admin_name,
            mobile=admin_mobile,
            password_hash=hash_password(admin_password),
            is_admin=True,
        )

        db.add(admin_user)
        db.commit()

        print("Admin user created successfully")

    except Exception as e:
        db.rollback()
        print("Failed to seed admin user:", e)

    finally:
        db.close()
