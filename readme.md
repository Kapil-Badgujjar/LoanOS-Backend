**HOW TO RUN**

- python -m venv .venv
- source .venv/bin/activate
- pip install -r requirements.txt
- uvicorn app.main:app --reload

---

**Admin Seed User**

An admin user is automatically created on first server startup.

Default Admin Credentials (from .env)

Mobile: 9876543210

Password: Admin@123


Admin seeding is idempotent — it runs safely on every startup without creating duplicates.

---

**Environment Variables**

Create a .env file in the backend root:

DATABASE_URL=postgresql://user:password@localhost:5432/loan_db

SECRET_KEY=supersecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

ADMIN_MOBILE=9876543210
ADMIN_PASSWORD=Admin@123
ADMIN_NAME=System Admin

CORS_ORIGINS=http://localhost:3000

---

**Backend runs at:**

http://127.0.0.1:8000


Health check:

GET /
