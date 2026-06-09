from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
from jose     import jwt, JWTError
from dotenv   import load_dotenv
import bcrypt
import os

#Загружаем переменные из .env
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
security = HTTPBearer()

def hash_password(password: str) -> str:  
    #Обрезаем начальную строку, превращаем в байты и добавляем "соль"
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password_plain: str, password_hashed: str) -> bool:
    #Убираем "соль" из хэша и сравниваем введённый пароль с тем, что лежит в БД
    return bcrypt.checkpw(password_plain.encode('utf-8'), password_hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload['exp'] = datetime.now() +timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
