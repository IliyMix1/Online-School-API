from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_simple():
    assert 1 + 1 == 2

# def test_get_all_students():
#     response = client.get('/students')
#     assert response.status_code == 200
