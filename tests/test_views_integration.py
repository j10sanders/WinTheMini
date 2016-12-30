import os
import unittest
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash

# Configure app to use the testing database
os.environ["CONFIG_PATH"] = "crossword.config.TravisConfig"
os.environ["CONFIG_PATH"] = "crossword.config.TestingConfig"

from crossword import app
from crossword.database import Base, engine, session, User, Entry

class TestAddEntry(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.client = app.test_client()
        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.fixtures = {
            'alice': User(name='Alice', email='alice@example.com',
                          password=generate_password_hash('alice'))}
        super(TestAddEntry, self).setUp()
    
    
    def simulate_login(self, user):
        with self.client.session_transaction() as http_session:
            http_session['user_id'] = str(user.id)
            http_session['_fresh'] = True
            
    def test_unauthenticated_add_entry(self):
        response = self.client.post('/entry/add', data={
            'title': '40',
            'content': 'Test Content'
        })
        self.assertEqual(response.status_code, 302)
        #self.assertIn('/entry/add', self.next_query_parameter(response.location))

    def test_add_entry(self):
        self.simulate_login(self.fixtures['alice'])
        response = self.client.post('/entry/add', data={
            'title': ':40',
            'content': 'Test Content'
        })

        self.assertEqual(response.status_code, 302)
        #self.assertEqual(urlparse(response.location).path, '/')

        entries = session.query(Entry).all()
        self.assertEqual(len(entries), 1)

        entry = entries[0]
        self.assertEqual(entry.title, '40')
        self.assertEqual(entry.content, 'Test Content')
        self.assertEqual(entry.author, self.fixtures['alice'])


        
    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)
        
if __name__ == "__main__":
    unittest.main()