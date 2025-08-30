from sqlalchemy.orm import Session 
from models import UserGame

class GameService:

    def __init__(self, user_id: int, session: Session):
        self.db = session
        self.user_id = user_id

    def start_daily_game(self) -> UserGame:
        pass 

