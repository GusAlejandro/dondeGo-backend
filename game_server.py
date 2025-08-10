from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager

import models, schemas
from database import Base, engine, get_db

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
