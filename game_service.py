from sqlalchemy.orm import Session, selectinload 
from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError
from models import UserGame, DailyGame, UserGuess, GameRound
from datetime import date 
from schemas import GameState, RoundPublic

class GameService:

    def __init__(self, session: Session):
        self.session = session


    def start_daily_game(self, user_id) -> GameState:
        today: date = date.date()
        # fetches the current game, will always return as long as daily_game exits 
        ug = self.get_or_create_user_game(today, user_id) 

        # derive game info via number of guesses 
        guess_count: int = self.session.scalar(select(func.count(UserGuess.id)).where(UserGuess.user_game_id==ug.id))
        curr_round: int = 5 if guess_count == 5 else guess_count + 1
        is_done: bool = True if guess_count == 5 else False


        # get the daily game in order to pull current round coordinates 
        curr_coords: RoundPublic = None
        daily_game: DailyGame = self.get_daily_game()
        if not is_done:
            curr_game_round = self.session.scalar(select(GameRound).where(
                GameRound.daily_game_id == daily_game.id, 
                GameRound.round_id == 3
            ))
            curr_coords = RoundPublic(latitude=curr_game_round.latitude, longitude=curr_game_round.longitude)


        # craft GameState object for response 
        game_state: GameState = GameState(daily_game_id=daily_game.id, current_round=curr_round, current_round_coordinates=curr_coords)
        return game_state
    
    def submit_guess(self) -> None:
        # TODO: Implement guess logic, it should calculate score, store it, and advance state of the game
        # TODO: Figure out if we will have a seperate endpoint to get current state or if it will be returned as part of this 
        pass 
    
    def get_daily_game(self) -> DailyGame:
        today: date = date.today()
        query: DailyGame = self.session.scalar_one_or_none(
            select(DailyGame).where(DailyGame.date == today).options(selectinload(DailyGame.rounds))
        )
        return query
        

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

            










