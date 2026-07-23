```python
import unittest
import requests

class TestWishlistIntegration(unittest.TestCase):
    BASE_URL = "http://localhost:5000"  # assumed base URL for the backend

    def setUp(self):
        # Sample user credentials
        self.credentials = {
            "username": "testuser",
            "password": "testpassword"
        }

        # Sample product ID to be used in tests
        self.product_id = 123

        # Log in the user and get a token
        response = requests.post(f"{self.BASE_URL}/login", json=self.credentials)
        self.assertEqual(response.status_code, 200)
        self.token = response.json().get('token')

        # Ensure token is received
        self.assertIsNotNone(self.token)

        # Add authorization header
        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }

    def test_add_item_to_wishlist(self):
        # Add product to wishlist
        response = requests.post(
            f"{self.BASE_URL}/wishlist/add",
            headers=self.headers,
            json={"product_id": self.product_id}
        )

        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())

    def test_remove_item_from_wishlist(self):
        # First add the product to the wishlist
        response = requests.post(
            f"{self.BASE_URL}/wishlist/add",
            headers=self.headers,
            json={"product_id": self.product_id}
        )
        self.assertEqual(response.status_code, 200)

        # Remove product from wishlist
        response = requests.post(
            f"{self.BASE_URL}/wishlist/remove",
            headers=self.headers,
            json={"product_id": self.product_id}
        )

        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())

    def test_view_wishlist(self):
        # View wishlist
        response = requests.get(
            f"{self.BASE_URL}/wishlist",
            headers=self.headers
        )

        # Verify the response
        self.assertEqual(response.status_code, 200)
        contents = response.json().get('wishlist_items')
        self.assertIsInstance(contents, list)

        # Assuming the test product was added before
        self.assertIn(self.product_id, [item['product_id'] for item in contents])

    def tearDown(self):
        # Log out user if there is an endpoint, otherwise skip
        pass

if __name__ == "__main__":
    unittest.main()
```

This code creates integration tests for adding, removing, and viewing products in a wishlist, verifying interactions between the frontend and backend in a simulated real-user environment.