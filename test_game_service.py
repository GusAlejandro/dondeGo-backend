import pytest
from sqlalchemy import create_engine
from datetime import date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from models import Base, DailyGame, UserGame, GameRound
from game_service import GameService

@pytest.fixture()
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    with SessionLocal() as s:
        yield s
    

@pytest.fixture()
def todays_game(session):
    dg = DailyGame(date=date.today())
    session.add(dg)
    session.flush()
    return dg


def test_get_or_create_when_create(session, todays_game):
    svc = GameService(session)

    # no current user game so we should expect the code to generate one where user_id == 1
    ug = svc.get_or_create_user_game(d=date.today(), user_id=1)
    assert isinstance(ug, UserGame)
    assert ug.id is not None
    assert ug.daily_game_id == todays_game.id
    assert ug.user_id == 1

def test_get_or_create_when_get(session, todays_game):
    svc = GameService(session)

    ug1 = svc.get_or_create_user_game(d=date.today(), user_id=42)
    ug2 = svc.get_or_create_user_game(d=date.today(), user_id=42)

    assert ug1.id == ug2.id
    assert session.query(UserGame).count() == 1


@pytest.fixture()
def todays_game_with_rounds(session):
    dg = DailyGame(date=date.today())
    session.add(dg)
    session.flush()

    rounds = []
    for r in range(1,6):
        gr = GameRound(
            round_id=r, 
            latitude=10.0+r, 
            longiturde=20.0+r,
            daily_game_id=dg.id
        )
        session.add(gr)
        rounds.append(gr)

    session.flush()
    return dg, rounds

