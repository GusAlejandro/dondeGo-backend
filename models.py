from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List
from database import Base

# class User(Base):
#     __tablename__ = "user"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
#     password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

#     games: Mapped[List["UserGame"]] = relationship(back_populates="user")


# class UserGame(Base):
#     __tablename__ = "user_game"

#     id: Mapped[int] = mapped_column(primary_key=True)

#     id = Column(Integer, primary_key=True)
#     user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     daily_game_id = Column(ForeignKey("daily_game.id", ondelete="CASCADE"), nullable=False)

# class UserGuess(Base):
#     __tablename__ = "user_guess"

#     id = Column(Integer, primary_key=True)
    

# class DailyGame(Base):
#     __tablename__ = "daily_game"

#     id = Column(Integer, primary_key=True)
#     game_date = Column(Date, unique=True, nullable=False)

#     rounds = relationship(
#         "GameRound",
#         cascade="all, delete-orphan",
#         order_by="GameRound.id",
#         lazy="selectin"
#     )

# class GameRound(Base):
#     __tablename__ = "game_rounds"

#     id = Column(Integer, primary_key=True)
#     lat = Column(Float, nullable=False)
#     long = Column(Float, nullable=False)

#     daily_game_id = Column(ForeignKey("daily_game.id", ondelete="CASCADE"), nullable=False)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    games: Mapped[List["UserGame"]] = relationship(
        "UserGame", 
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UserGame(Base):
    __tablename__ = "user_game"
    __table_args__ = (
        UniqueConstraint("user_id", "daily_game_id", name="uq_user_dailygame"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    daily_game_id: Mapped[int] = mapped_column(ForeignKey("daily_game.id"))

    user: Mapped["User"] = relationship(back_populates="games")
    daily_game: Mapped["DailyGame"] = relationship()
    guesses: Mapped[List["UserGuess"]] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UserGuess(Base):
    __tablename__ = "user_guess"

    id: Mapped[int] = mapped_column(primary_key=True)
    round_id: Mapped[int] = mapped_column()
    user_game_id: Mapped[int] = mapped_column(ForeignKey("user_game.id", ondelete="CASCADE"))
    game_round_id: Mapped[int] = mapped_column(ForeignKey("game_round.id"))

    # UserGuess is for a GameRound of the DailyGame
    game_round: Mapped["GameRound"] = relationship()



class DailyGame(Base):
    __tablename__ = "daily_game"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[Date] = mapped_column(Date, unique=True)
    rounds: Mapped[List["GameRound"]] = relationship(
        back_populates="daily_game",
        cascade="all, delete-orphan",
        passive_deletes=True,   
    )


class GameRound(Base):
    __tablename__ = "game_round"

    id: Mapped[int] = mapped_column(primary_key=True)
    round_id: Mapped[int] = mapped_column()
    daily_game_id: Mapped[int] = mapped_column(ForeignKey("daily_game.id", ondelete="CASCADE"))
    
    daily_game: Mapped["DailyGame"] = relationship(back_populates="rounds")

