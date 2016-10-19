import unittest
import os
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Python 2 compatibility

# Configure app to use the testing databse
os.environ["CONFIG_PATH"] = "crossword.config.TravisConfig"
os.environ["CONFIG_PATH"] = "crossword.config.TestingConfig"

from crossword import app
from crossword import models
from crossword.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the crossword API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

if __name__ == "__main__":
    unittest.main()
