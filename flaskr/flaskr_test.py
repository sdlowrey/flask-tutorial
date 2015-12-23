import flaskr
import os
import tempfile
import unittest

class FlaskrTestCase(unittest.TestCase):
    """A simple test case for the flaskr app.

    Database is assumed to be local sqlite3 (file) and is initialized/destroyed during the test.
    """
    def setUp(self):
        """Initialize the database in a temp file, create a test app, and initialize the DB"""
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        flaskr.init_db()

    def tearDown(self):
        """Close the database file and delete it."""
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        """Send an HTTP GET to the root URL and verify the message that comes back."""
        rv = self.app.get('/')
        self.assertNotIn('No entries here so far', rv.data)

    def login(self, username, password):
        """Login so admin functions can be tested."""
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        self.assertIn('You were logged in', rv.data)
        rv = self.logout()
        self.assertIn('You were logged out', rv.data)
        rv = self.login('adminx', 'default')
        self.assertIn('Invalid username', rv.data)
        rv = self.login('admin', 'defaultx')
        self.assertIn('Invalid password', rv.data)

    def test_messages(self):
        """Add a new record to the database. Verify that HTML is allowed in the text but not the title."""
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        self.assertNotIn('No entries found', rv.data)
        self.assertIn('&lt;Hello&gt;', rv.data)
        self.assertIn('<strong>HTML</strong> allowed here', rv.data)

if __name__ == '__main__':
    unittest.main()