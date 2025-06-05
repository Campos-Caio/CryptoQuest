import unittest
from backend.app.models.user import User
from datetime import date

class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User(1, 'Caio', 'caio@gmail', '1234', date(2020, 10, 10), '1')
    
    def loginTest(self):
        self.assertTrue(self.user.fazerLogin('caio@gmail', '1234'))
    
    def incorrectLoginTest(self): 
        self.assertFalse(self.user.fazerLogin('caio@gmail', '123'))
    
    def editProfileTest(self):
        self.user.profileEdit('Novo Caio')
        self.assertEqual(self.user.name, 'Novo Caio')

if __name__ == '__main__':
    unittest.main()