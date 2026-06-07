from fastapi.testclient import TestClient
from main import app

from database import get_session, get_session_test

#Подменяем сессию на тестовую, чтобы все запросы отправлялись в тестовую БД
app.dependency_overrides[get_session] = get_session_test

client = TestClient(app)

def test_simple():
    assert 1 + 1 == 2

def test_reg():
    response = client.post('/auth/reg', json={"first_name": 'Jane', "last_name": 'Doe', "email": 'test123@gmail.com', "password": 'test12345'})
    assert response.status_code == 200

# def test_get_all_students():
#     response = client.get('/students')
#     assert response.status_code == 200
