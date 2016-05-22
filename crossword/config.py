import os
class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI =  os.environ["DATABASE_URL"]
    DEBUG = True
    SECRET_KEY = "Not secret"
