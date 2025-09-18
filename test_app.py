import unittest
from app import app

class IncidentTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_homepage_loads(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    def test_login_page_loads(self):
        result = self.app.get('/login')
        self.assertIn(b'Login', result.data)

if __name__ == '__main__':
    unittest.main()
