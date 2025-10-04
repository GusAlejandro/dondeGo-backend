from sqlalchemy.orm import Session, selectinload 
from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError
from models import UserGame, DailyGame, UserGuess, GameRound
from datetime import date 
from schemas import GameState, Coordinate, GuessResponse, GuessRequest
import math

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
        curr_coords: Coordinate = None
        daily_game: DailyGame = self.get_daily_game()
        if not is_done:
            curr_game_round = self.session.scalar(select(GameRound).where(
                GameRound.daily_game_id == daily_game.id, 
                GameRound.round_id == 3
            ))
            curr_coords = Coordinate(latitude=curr_game_round.latitude, longitude=curr_game_round.longitude)


        # craft GameState object for response 
        game_state: GameState = GameState(daily_game_id=daily_game.id, current_round=curr_round, current_round_coordinates=curr_coords)
        return game_state
    
    def submit_guess(self, user_id: int, guess: GuessRequest) -> GuessResponse:
        daily_game: DailyGame = self.get_daily_game()
        curr_round: GameRound = self.session.scalar(select(GameRound).where(
            GameRound.daily_game_id == daily_game.id,
            GameRound.round_id == guess.round
        ))

        actual: Coordinate = Coordinate(latitude=curr_round.latitude, longitude=curr_round.longitude)

        score: int = GameService.calculate_score(guess.guess, actual)

        user_game: UserGame = self.session.scalar(
            select(UserGame).where(
                and_(UserGame.user_id == user_id, UserGame.daily_game_id == daily_game.id)
            )
        )

        user_guess: UserGuess = UserGuess(round_id=curr_round.id, user_game_id = user_game.id, game_round_id=curr_round.id, score=score)

        self.session.add(user_guess)
        self.session.flush()

        # advance game state 
        is_done: bool = True if curr_round.round_id = 5 else False
        new_coordinates: Coordinate = None
        if not is_done:
            next_round: GameRound = self.session.scalar(select(GameRound).where(
                GameRound.daily_game_id == daily_game.id,
                GameRound.round_id == curr_round.round_id + 1
            ))
            new_coordinates.longitude = next_round.longitude
            new_coordinates.latitude = next_round.latitude

        new_game_state: GameState = GameState(daily_game_id=daily_game.id, completed=is_done, current_round=next_round.round_id, current_round_coordinates=new_coordinates)
        return GuessResponse(score=score, game_state=new_game_state)

        



        

    @staticmethod
    def calculate_score(guess: Coordinate, actual: Coordinate) -> int:
        max_score = 5000
        d_half_km = 1000   # ~half points at 1000 km
        d_max_km = 9000    # beyond this = zero
        full_score_under_m = 25

        d = GameService.haversine_km(
            guess.latitude, guess.longitude,
            actual.latitude, actual.longitude
        )

        # Perfect score for very close guesses
        if d <= full_score_under_m / 1000:
            return max_score

        # Hard zero for way-off guesses
        if d >= d_max_km:
            return 0

        # Exponential decay
        k = math.log(2) / d_half_km
        score = max_score * math.exp(-k * d)

        return int(round(score))
    
    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0  # Earth radius in km
        lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
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

            










