from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String[50], unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

