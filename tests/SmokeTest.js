import pytest
from flask import Flask
from werkzeug.exceptions import NotFound

# Sample Flask application for testing
app = Flask(__name__)

@app.route('/login', methods=['POST'])
async def login():
    return {"status": "success"}, 200

@app.route('/products', methods=['GET'])
async def get_products():
    return {"products": []}, 200

# Integration test class for Flask 3.x compatibility
class TestFlaskApp:
    
    @pytest.mark.asyncio
    async def test_login(self, client):
        response = await client.post('/login', json={"username": "test", "password": "test"})
        assert response.status_code == 200
        assert response.json == {"status": "success"}

    @pytest.mark.asyncio
    async def test_get_products(self, client):
        response = await client.get('/products')
        assert response.status_code == 200
        assert response.json == {"products": []}

    async def test_non_existent_route(self, client):
        response = await client.get('/non-existent-route')
        assert response.status_code == 404
        assert response.json == {"error": "Not Found"}

@pytest.fixture
async def client():
    async with app.test_client() as client:
        yield client

# Additional tests can be added for session management and middleware checks if necessary.