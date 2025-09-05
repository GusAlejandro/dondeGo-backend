from datetime import date, datetime
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from database import Base

DATABASE_URI = "sqlite:///./app.db"

# TODO: Write a scrpt that will add a DailyGame object to the database with 
# 5 GameRound objects 

engine: Engine = create_engine(DATABASE_URI, future=False)

SessionLocal: sessionmaker[Session] = sessionmaker(bind=engine)
session: Session = SessionLocal()

Base.metadata.create_all(engine)



