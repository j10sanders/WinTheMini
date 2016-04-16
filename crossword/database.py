from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from crossword import app

engine = create_engine(app.config["DATABASE_URI"])
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
