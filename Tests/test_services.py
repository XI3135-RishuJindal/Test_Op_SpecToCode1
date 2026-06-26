import unittest
from domain.services import UserService

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.service = UserService()

    def test_create_user(self):
        user = self.service.create_user(1, "John Doe", "john.doe@example.com")
        self.assertEqual(user.name, "John Doe")

if __name__ == '__main__':
    unittest.main()
