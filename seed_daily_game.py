from datetime import date, datetime
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from database import Base
from models import DailyGame, GameRound

DATABASE_URI = "sqlite:///./app.db"

# TODO: Write a scrpt that will add a DailyGame object to the database with 
# 5 GameRound objects 

engine: Engine = create_engine(DATABASE_URI, future=True)

SessionLocal: sessionmaker[Session] = sessionmaker(bind=engine)
session: Session = SessionLocal()

Base.metadata.create_all(engine)


today: date = date.today()

# check if game for today's date already exists 

existing: bool = session.query(DailyGame).filter(DailyGame.date == today).first()

if existing:
    print(f"DailyGame for {today} already exists...")
    exit()

new_game: DailyGame = DailyGame(date = today)
session.add(new_game)
session.flush()


r1: GameRound =  GameRound(round_id = 1, latitude=48.86290198191819, longitude=2.2933190395279, daily_game = new_game) # 48.86290198191819, 2.2933190395279
r2: GameRound =  GameRound(round_id = 2, latitude=41.397015615516594, longitude=2.17582511080004, daily_game = new_game) # 41.397015615516594, 2.17582511080004
r3: GameRound =  GameRound(round_id = 3, latitude=59.93366696116407, longitude=30.307116878580366, daily_game= new_game) # 59.93366696116407, 30.307116878580366
r4: GameRound =  GameRound(round_id = 4, latitude=43.71093981199275, longitude=7.335553392882501, daily_game= new_game) # 43.71093981199275, 7.335553392882501
r5: GameRound =  GameRound(round_id = 5, latitude=44.432768249092206, longitude=26.103351344148383, daily_game = new_game) # 44.432768249092206, 26.103351344148383

session.add_all([r1, r2, r3, r4, r5])
session.commit()

print(f"New game and game rounds have been seeded..")
