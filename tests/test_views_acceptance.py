import os
import unittest
import multiprocessing
import time
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash
from splinter import Browser

# Configure app to use the testing database
os.environ["CONFIG_PATH"] = "crossword.config.TravisConfig"
os.environ["CONFIG_PATH"] = "crossword.config.TestingConfig"

from crossword import app
from crossword.database import Base, engine, session, User

'''I'm getting an integrity error. https://trac.edgewall.org/ticket/8575  Commenting out these tests until I can figure it out.'''
class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.browser = Browser("phantomjs")

        # Set up the tables in the database
        Base.metadata.create_all(engine)
        
        #session.execute("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users_name_key)+1)")

        #success = simplejson.dumps({'success':'success',})

        # Create an example user
        self.user = User(name="AliceW", email="alicewl@example.com",
                         password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

        self.process = multiprocessing.Process(target=app.run,
                                               kwargs={"port": 8080})
        self.process.start()
        time.sleep(1)


    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        self.process.terminate()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)
        self.browser.quit()

    def test_login_correct(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "alicewl@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")

    def test_login_incorrect(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "bob@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login")


if __name__ == '__main__':
    unittest.main()
