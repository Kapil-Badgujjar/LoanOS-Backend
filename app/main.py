import os
from fastapi import FastAPI
from app.database import Base, engine
from app import models  # <-- important
from app.routers import auth, application, kyc, credit, eligibility, admin
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.seed import seed_admin_user

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    seed_admin_user()
    yield
    # Shutdown (optional)


app = FastAPI(title="Loan Origination System")

origins = os.getenv("CORS_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(application.router)
app.include_router(kyc.router)
app.include_router(credit.router)
app.include_router(eligibility.router)
app.include_router(admin.router)

# @app.on_event("startup")
# def startup_event():
#     seed_admin_user()

@app.get("/")
def health():
    return {"status": "ok"}
