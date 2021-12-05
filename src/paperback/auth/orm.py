from sqlalchemy import Column, ForeignKey, Integer, String, Text, LargeBinary
from sqlalchemy.orm import relationship

from paperback.auth.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, unique=True, primary_key=True)

    username = Column(String, unique=True)
    hashed_password = Column(Text)

    email = Column(String, unique=True, nullable=True)

    level_of_access = Column(Integer)

    tokens = relationship("Token")


class Token(Base):
    __tablename__ = "tokens"

    token_uuid = Column(LargeBinary(16), primary_key=True, unique=True)
    issued_at = Column(Text)

    issued_by = relationship("User")
