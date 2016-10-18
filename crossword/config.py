import os
class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://ubuntu:thinkful@localhost:5432/newcrossword"
    DEBUG = True
    SECRET_KEY = os.environ.get("CROSSWORD_SECRET_KEY", os.urandom(12))
  
  

class TestingConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://ubuntu:thinkful@localhost:5432/crossword-test"
    DEBUG = False
    SECRET_KEY = "Not secret"
    
'''
import os
class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://ubuntu:thinkful@localhost:5432/newcrossword"
    DEBUG = True
    SECRET_KEY = os.environ.get("CROSSWORD_SECRET_KEY", os.urandom(12))
    DEBUG = True
    SECRET_KEY = "Not secret"
    
import os
class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI =  os.environ["DATABASE_URL"]
    DEBUG = True
    SECRET_KEY = os.environ.get("CROSSWORD_SECRET_KEY", os.urandom(12))
    
import os
class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://ubuntu:thinkful@localhost:5432/newcrossword"
    DEBUG = True
    SECRET_KEY = os.environ.get("CROSSWORD_SECRET_KEY", os.urandom(12))
'''

