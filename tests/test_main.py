from fastapi.testclient import TestClient
from main import app

from database import get_session, get_session_test, create_record

import random

#Подменяем сессию на тестовую, чтобы все запросы отправлялись в тестовую БД
app.dependency_overrides[get_session] = get_session_test

client = TestClient(app)


def generate_filler(num: int) -> str:
    '''Создаёт случайный наполнитель для различных полей'''
    symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    filler = ''
    for i in range(num):
        filler += random.choice(symbols)

    return filler


def test_simple():
    assert 1 + 1 == 2

def test_reg():
    '''Проверяем эндпоинт регистрации'''
    response = client.post('/auth/reg', json={
        "first_name": f'name_{generate_filler(15)}', 
        "last_name":  f'surname_{generate_filler(15)}', 
        "email":      f'user_{generate_filler(20)}@gmail.com', 
        "password":    'test12345'
        })
    assert response.status_code == 200

def test_login():
    '''Проверяем эндпоинт логина'''
    response = client.post('/auth/login', json={
        "email": 'adminROOT@gmail.com',
        "password": 'Admin12345'
    })
    print(response.json())
    assert response.status_code == 200
