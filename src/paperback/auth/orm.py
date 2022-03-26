from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from paperback.auth.database import Base


class User(Base):
    __tablename__ = "user"

    user_uuid = Column(
        UUID(as_uuid=True), unique=True, primary_key=True, default=uuid4, index=True
    )

    username = Column(String, unique=True)
    hashed_password = Column(Text)

    email = Column(String, unique=True, nullable=True)

    level_of_access = Column(Integer)

    tokens = relationship("Token", back_populates="user")


class Token(Base):
    __tablename__ = "token"

    token_uuid = Column(
        UUID(as_uuid=True), primary_key=True, unique=True, default=uuid4, index=True
    )
    issued_at = Column(DateTime, default=datetime)

    user_uuid = Column(UUID(as_uuid=True), ForeignKey("user.user_uuid"))
    user = relationship("User", back_populates="tokens")
