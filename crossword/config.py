class DevelopmentConfig(object):
    DATABASE_URI = "postgresql://ubuntu:thinkful@localhost:5432/crossword"
    DEBUG = True

class TestingConfig(object):
    DATABASE_URI = "postgresql://ubuntu:thinkful@localhost:5432/crossword-test"
    DEBUG = True
