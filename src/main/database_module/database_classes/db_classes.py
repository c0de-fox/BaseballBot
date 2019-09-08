from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from src.main.db_session import DatabaseSession

Base = declarative_base()

class Play(Base):
    __tablename__ = 'play'

    play_id = Column(String, nullable=False, primary_key=True)
    pitch_value = Column(Integer, nullable=True)
    swing_value = Column(Integer, nullable=False)
    creation_date = Column(Date, nullable=False)

    guesses = relationship(lambda : Guess)

class Guess(Base):
    __FAKE_VALUE__ = -5000

    __tablename__ = 'guess'
    member_id = Column(String, nullable=False, primary_key=True)
    play_id = Column(UUID, ForeignKey(Play.play_id), nullable=False, primary_key=True)
    guessed_number = Column(Integer, nullable=False)
    member_name = Column(String, nullable=False)
    difference = Column(Integer)

    play = relationship("Play", back_populates="guesses")
