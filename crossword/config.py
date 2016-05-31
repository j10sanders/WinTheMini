import os
class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI =  os.environ["DATABASE_URL"]
    DEBUG = True
    SECRET_KEY = os.environ.get("CROSSWORD_SECRET_KEY", os.urandom(12))


'''import os
class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI =  os.environ["DATABASE_URL"]
    DEBUG = True
    SECRET_KEY = "Not secret"
    
import os
class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://ubuntu:thinkful@localhost:5432/crossword"
    DEBUG = True
    SECRET_KEY = os.environ.get("CROSSWORD_SECRET_KEY", os.urandom(12))'''
