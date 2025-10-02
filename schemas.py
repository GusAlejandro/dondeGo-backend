from pydantic import BaseModel, constr

class RegisterIn(BaseModel):
    username: constr(strip_whitespace=True, min_length=3, max_length=50)
    password: constr(min_length=1)

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class LoginIn(BaseModel):
    username: constr(strip_whitespace=True, min_length=3, max_length=50)
    password: constr(min_length=1)


class AccessTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StartGameRequest(BaseModel):
    game_mode: bool = None

class RoundPublic(BaseModel):
    latitude: float
    longitude: float

class GameState(BaseModel):
    daily_game_id: int
    completed: bool
    current_round: int 
    current_round_coordinates: RoundPublic





