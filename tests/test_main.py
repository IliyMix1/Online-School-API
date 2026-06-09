from fastapi.testclient import TestClient
from main import app
from database import get_session, get_session_test, create_record
import random
import pytest

#Подменяем сессию на тестовую, чтобы все запросы отправлялись в тестовую БД
app.dependency_overrides[get_session] = get_session_test

client = TestClient(app)
client.raise_server_exceptions = True 


def generate_filler(num: int) -> str:
    '''Создаёт случайный наполнитель для различных полей'''
    symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    filler = ''
    for i in range(num):
        filler += random.choice(symbols)

    return filler


@pytest.fixture
def reg_user():
    '''Регистрируем аккаунт со случайными данными'''
    reg_data = {
        "first_name": f'name_{generate_filler(15)}', 
        "last_name":  f'surname_{generate_filler(15)}', 
        "email":      f'user_{generate_filler(20)}@gmail.com', 
        "password":    'test12345'
       }
    
    client.post('/auth/reg', json=reg_data)
    return reg_data

@pytest.fixture
def login_admin():
    '''Логинимся от лица администратора'''
    login_data = {
        "email": 'adminROOT@gmail.com',
        "password": 'Admin12345'
    }
    response = client.post('/auth/login', json=login_data)
    
    #Превращаем полученный json в словарь
    data = response.json()
    #Возвращаем токен
    yield data['access_token']


def test_simple():
    '''Проверяем, работают ли вообще тесты'''
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


def test_login(reg_user):
    '''Проверяем эндпоинт логина'''
    response = client.post('/auth/login', json={
        'email': reg_user['email'],
        'password': reg_user['password']
    })

    assert response.status_code == 200

def test_create_course(login_admin):
    '''Проверяем создаётся ли курс'''
    #Получаем токен из фикстуры и смотрим успешно ли залогинились
    token = login_admin
    assert token is not None

    #Передаём токен в заголовки
    headers = {'Authorization': f'Bearer {token}'}

    #Пытаемся создать курс
    response = client.post('/admin/courses', 
    json={"name": f'course {generate_filler(15)}'},
    headers=headers)

    assert response.status_code == 200