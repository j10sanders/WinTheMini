from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from . import app

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Table, Boolean
from .database import Base, engine
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask.ext.login import UserMixin

followers = Table('followers', Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id')),
    Column('followed_id', Integer, ForeignKey('users.id'))
)


class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    email = Column(String(128), unique=True)
    password = Column(String(128))
    entries = relationship("Entry", backref="author")
    followed = relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=backref('followers', lazy='dynamic'),
                               lazy='dynamic')
                               
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self
        return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self
    
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    


class Entry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True)
    title = Column(Integer)
    content = Column(Text)
    datetime = Column(DateTime(timezone=True), default=datetime.datetime.now)
    day_rank = Column(Integer)
    author_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User, lazy='joined')
    
    
class PWReset(Base):
    __tablename__ = "pwreset"
    id = Column(Integer, primary_key=True)
    reset_key = Column(String(128), unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    datetime = Column(DateTime(timezone=True), default=datetime.datetime.now)
    user = relationship(User, lazy='joined')
    has_activated = Column(Boolean, default=False)

    
    
'''class DayResults(Base):
    __tablename__ = "dayresults"
    id = Column(Integer, primary_key=True)
    winner_id =Column(Integer, ForeignKey('users.id'))'''
    
    
    
Base.metadata.create_all(engine)