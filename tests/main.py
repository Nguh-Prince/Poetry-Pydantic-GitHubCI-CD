import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_item(client):
    response = client.post('/items', json={'name': 'Item1', 'price': 10.99})
    assert response.status_code == 201
    assert response.json == {'name': 'Item1', 'price': 10.99}

def test_create_item_validation_error(client):
    response = client.post('/items', json={'name': 'Item1', 'price': 'invalid'})
    assert response.status_code == 400
    assert 'price' in response.json[0]['loc']
