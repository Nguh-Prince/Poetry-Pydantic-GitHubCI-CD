import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register(client):
    # Test registration
    rv = client.post('/register', data=dict(
        email='newuser@example.com',
        name='newuser',
        password='password123'
    ), follow_redirects=True)
    assert b'Redirecting...' in rv.data

def test_login(client):
    # Test login
    rv = client.post('/login', data=dict(
        email='user1@example.com',
        password='password1'
    ), follow_redirects=True)
    assert b"Logged in as user1" in rv.data

    # Test incorrect password
    rv = client.post('/login', data=dict(
        email='user1@example.com',
        password='wrongpassword'
    ), follow_redirects=True)
    assert b"Login failed. Invalid credentials." in rv.data