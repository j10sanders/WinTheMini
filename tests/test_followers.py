import os
import unittest
import multiprocessing
import time
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash
from splinter import Browser

# Configure app to use the testing database
os.environ["CONFIG_PATH"] = "crossword.config.TravisConfig"
#os.environ["CONFIG_PATH"] = "crossword.config.TestingConfig"


from crossword import app
from crossword.database import Base, engine, session, User, Entry

from datetime import datetime, timedelta

#...
class TestCase(unittest.TestCase):
    
    
    #...
    def test_followers(self):
        # make four users
        u1 = User(name='ptest1', email='ptest1@gmail.com')
        u2 = User(name='ptest2', email='ptest2@gmail.com')
        u3 = User(name='ptest3', email='ptest3@gmail.com')
        u4 = User(name='ptest4', email='ptest4@gmail.com')
        session.add(u1)
        session.add(u2)
        session.add(u3)
        session.add(u4)
        # setup the followers
        u1.follow(u1)
        u1.follow(u2) 
        u1.follow(u4)  
        u2.follow(u2) 
        u2.follow(u3) 
        u3.follow(u3) 
        u3.follow(u4)  
        u4.follow(u4) 
        session.add(u1)
        session.add(u2)
        session.add(u3)
        session.add(u4)
        session.commit()
        # check the the amount of followers for each user
        #assert u1.follow(u2) is None
        assert u1.is_following(u2)
        assert u1.followers.count() == 1
        self.assertEqual(u1.followers.first().name, 'ptest1')
        self.assertEqual(u2.followers.count(), 2)
        self.assertEqual(u2.followers.first().name, 'ptest1')
        u = u1.unfollow(u2)
        assert u is not None
        session.add(u)
        session.commit()
        assert not u1.is_following(u2)
        assert u1.followed.count() == 2
        assert u2.followed.count() == 2
        
        
    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)

        
if __name__ == "__main__":
    unittest.main()