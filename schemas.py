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


class GameStartIn(BaseModel):
    pass 
