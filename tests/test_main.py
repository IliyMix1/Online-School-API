from fastapi.testclient import TestClient
from main import app
from database import get_session, get_session_test
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
def get_auth_client(reg_user):
    '''Логинимся от лица студента/администратора и сразу же передаём токен в заголовок'''
    def _login(role: str):
        if role == 'admin':
            login_data = {"email": 'adminROOT@gmail.com', "password": 'Admin12345'}
        else:
            login_data = {"email": reg_user['email'], "password": reg_user['password']}
    
        response = client.post('/auth/login', json=login_data)
    
        #Превращаем полученный json в словарь
        data = response.json()
        token = data['access_token']

        #Привязываем токен к клиенту
        client.headers.update({'Authorization': f'Bearer {token}'})
        return client
    
    yield _login #data['access_token']

    #После теста очищаем заголовки, чтобы случайно не помешать другим тестам
    client.headers.pop('Authorization', None)


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

def test_reg_with_existing_email(reg_user):
    '''Проверям вылетает ли ошибка, если используют уже занятый email'''
    response = client.post('/auth/reg', json={
        "first_name": reg_user['first_name'],
        "last_name":  reg_user['last_name'], 
        "email":      reg_user['email'], 
        "password":   'test12345'
    })

    assert response.status_code == 409



def test_login(reg_user):
    '''Проверяем эндпоинт логина'''
    response = client.post('/auth/login', json={
        'email': reg_user['email'],
        'password': reg_user['password']
    })

    assert response.status_code == 200

def test_login_wrong_password(reg_user):
    '''Проверяем вылетает ли ошибка при неверном пароле'''
    response = client.post('/auth/login', json={
        'email': reg_user['email'],
        'password': 'testtesttest'
    })

    assert response.status_code == 401

def test_login_non_existing_email(reg_user):
    '''Провермяем вылетает ли ошибка, если email не существует'''
    response = client.post('/auth/login', json={
        'email': 'testtesttest',
        'password': reg_user['password']
    })

    assert response.status_code == 401



def test_admin_can_create_course(get_auth_client):
    '''Проверяем создаётся ли курс'''
    admin_client = get_auth_client('admin')

    #Пытаемся создать курс
    response = admin_client.post('/admin/courses', json={"name": f'course {generate_filler(15)}'})

    assert response.status_code == 200

def test_student_cannot_create_course(get_auth_client):
    '''Проверяем есть ли у студентов возможность создать курс(её быть не должно)'''
    student_client = get_auth_client('student')

    response = student_client.post('/admin/courses', json={"name": f'course {generate_filler(15)}'})

    assert response.status_code == 403  

def test_user_can_buy_course(get_auth_client):
    student_client = get_auth_client('student')

    course_id = random.randint(1, 9)
    tariffs = ('mini', 'standard', 'pro')

    response = student_client.post(f'/courses/{course_id}/buy', json={
        'tariff': random.choice(tariffs)
    })

    assert response.status_code == 200

def test_user_cannot_buy_same_course_twice(get_auth_client):
    student_client = get_auth_client('student')

    course_id = random.randint(1, 9)
    tariffs = ('mini', 'standard', 'pro')
    tariff = random.choice(tariffs)

    response = student_client.post(f'/courses/{course_id}/buy', json={
        'tariff': tariff
    })
    response = student_client.post(f'/courses/{course_id}/buy', json={
        'tariff': tariff
    })

    assert response.status_code == 409