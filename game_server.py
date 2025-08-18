from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import hashlib, uuid
from jose import jwt
import models, schemas
from database import Base, engine, get_db

JWT_SECRET = "dev-secret-change-me"
JWT_ALG = "HS256"
ACCESS_TTL_SECONDS = 10 * 60
REFRESH_TTL_DAYS = 14

def _now():
    return datetime.now(timezone.utc)

def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def create_access_token(user_id: int) -> str:
    now = _now()
    payload = {
        "sub": str(user_id),
        "jlti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ACCESS_TTL_SECONDS)).timestamp())
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def verify_password(plain: str, pw_hash: str) -> bool:
    return pwd_ctx.verify(plain, pw_hash)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield 


app = FastAPI(lifespan=lifespan)
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Coordinate(BaseModel):
    latitude: float
    longitude: float

@app.get("/coordinates", response_model=List[Coordinate])
async def get_coordinates():
    coords = [
        {"latitude": 37.7749, "longitude": -122.4194},  # San Francisco
        {"latitude": 34.0522, "longitude": -118.2437},  # Los Angeles
        {"latitude": 40.7128, "longitude": -74.0060},   # New York
        {"latitude": 51.5074, "longitude": -0.1278},    # London
        {"latitude": 35.6895, "longitude": 139.6917},   # Tokyo
    ]
    return coords

@app.post("/register", response_model=schemas.UserOut)
def register(payload: schemas.RegisterIn, db: Session = Depends(get_db)):

    get_existing = db.execute(
        select(models.User).where(models.User.username == payload.username)
    ).scalar_one_or_none()

    if get_existing:
        raise HTTPException(status_code=409, detail="Username already taken")
    
    hashed_pwd = pwd_ctx.hash(payload.password)
    user = models.User(username=payload.username, password_hash=hashed_pwd)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user 

@app.post("/login", response_model=schemas.AccessTokenOut)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.execute(
        select(models.User).where(models.User.username == payload.username)
    ).scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    access = create_access_token(user.id)

    return {"access_token": access}


