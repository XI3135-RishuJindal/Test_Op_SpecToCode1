import unittest
from domain.user import User

class TestUser(unittest.TestCase):
    def test_user_creation(self):
        user = User(user_id=1, name="John Doe", email="john.doe@example.com")
        self.assertEqual(user.name, "John Doe")

if __name__ == '__main__':
    unittest.main()
