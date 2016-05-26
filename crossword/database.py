from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from . import app

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], connect_args={"options": "-c timezone=est"})
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from .database import Base, engine
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask.ext.login import UserMixin

class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    email = Column(String(128), unique=True)
    password = Column(String(128))
    entries = relationship("Entry", backref="author")

class Entry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True)
    title = Column(Integer)
    content = Column(Text)
    datetime = Column(DateTime(timezone=True), default=datetime.datetime.now)
    #day_rank = Column(Integer)
    author_id = Column(Integer, ForeignKey('users.id'))

    
'''class DayResults(Base):
    __tablename__ = "dayresults"
    id = Column(Integer, primary_key=True)
    winner_id =Column(Integer, ForeignKey('users.id'))'''
    
    
    
Base.metadata.create_all(engine)