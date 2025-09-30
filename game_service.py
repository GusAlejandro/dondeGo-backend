from sqlalchemy.orm import Session 
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from models import UserGame, DailyGame
from datetime import date 

class GameService:

    def __init__(self, session: Session):
        self.session = session


    def start_daily_game(self, user_id) -> UserGame:
        today: date = date.date()
        ug = self.get_or_create_user_game(today, user_id) 
        # look into eager-loading the daily game, current guesses, etc 
        return ug 
    
    def submit_guess(self) -> None:
        # TODO: Implement guess logic, it should calculate score, store it, and advance state of the game
        # TODO: Figure out if we will have a seperate endpoint to get current state or if it will be returned as part of this 
        pass 
        

    def get_or_create_user_game(self, d: date, user_id: int) -> UserGame:

        # fetch the global current daily game:
        daily_game: DailyGame = self.session.execute(
            select(DailyGame).where(DailyGame.game_date == d)
        ).scalar_one_or_none()

        if daily_game is None:
            raise ValueError("No Daily Game has been set, run the seedeing script")

        user_game: UserGame = self.session.execute(
            select(UserGame).where(
                and_(UserGame.user_id == user_id, UserGame.daily_game_id == daily_game.id)
            )
        ).scalar_one_or_none()

        if user_game:
            # user has existing game, return current game object 
            return user_game
        
        new_user_game = UserGame(user_id = user_id, daily_game=daily_game)
        self.session.add(new_user_game)

        try: 
            self.session.flush()
            return new_user_game
        except IntegrityError:
            self.session.rollback()
            # another request made in parallel, fetch the existing one 
            ug: UserGame = self.session.execute(select(UserGame).where(and_(UserGame.user_id == user_id, UserGame.daily_game_id == daily_game.id))).scalar_one_or_none()
        return ug 

            










