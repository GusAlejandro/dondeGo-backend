from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import hashlib, uuid
from jose import jwt
import models, schemas
from database import Base, engine, get_db
from typing import Dict, Any 
from fastapi.security import OAuth2PasswordBearer
from game_service import GameService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ACCESS_TTL_SECONDS)).timestamp())
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def verify_password(plain: str, pw_hash: str) -> bool:
    return pwd_ctx.verify(plain, pw_hash)

def decode_access_token(token: str) -> Dict[str, Any]:
    payload = jwt.decode(
        token, key=JWT_SECRET, algorithms=[JWT_ALG], 
        options={
            "require": ["sub", "jti", "iat", "exp"],
            "verify_signature": True,
            "verify_exp": True,
            "verify_iat": True,
        },
    )
    return payload


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise ValueError("Missing sub")
        user_id = int(sub)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user

def get_game_service(db: Session = Depends(get_db)) -> GameService:
    game_svc: GameService = GameService(db)
    return game_svc


@asynccontextmanager
async def lifespan(app: FastAPI):
    from database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield 


app = FastAPI(lifespan=lifespan)
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


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

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # handles case if user w/matching username created after check 
        raise HTTPException(status_code=409, detail="Username already taken")

    db.refresh(user)
    return user 

@app.post("/login", response_model=schemas.AccessTokenOut)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.execute(
        select(models.User).where(models.User.username == payload.username)
    ).scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid Credentials", headers={"WWW-Authenticate": "Bearer"})
    
    access = create_access_token(user.id)

    return {"access_token": access}


@app.post('/start_game', response_model=schemas.GameState)
def start_game(payload: schemas.StartGameRequest, session: Session = Depends(get_db), user: models.User = Depends(get_current_user), game_svc: GameService = Depends(get_game_service)):
    game: schemas.GameState = game_svc.start_daily_game(user.id)
    return game

@app.post('/submit_guess', response_model=schemas.GuessResponse)
def submit_guess(payload: schemas.GuessRequest, session: Session = Depends(get_db), user: models.User = Depends(get_current_user), game_svc: GameService = Depends(get_game_service):
    return game_svc.submit_guess(user.id, payload)