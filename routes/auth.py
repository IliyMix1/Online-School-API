#Для эндпоинтов
from fastapi                import APIRouter, Depends, HTTPException
from schemas.schemas        import AuthReg, AuthLogin, AuthUserCreate, AuthStudentCreate
#Для интеграции с PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm         import joinedload
from sqlalchemy             import select
from database               import get_session, select_record, create_record
from models.models          import User, Student

from auth                   import verify_password, hash_password, create_access_token

auth_router = APIRouter(prefix='/auth', tags=['Auth'])

@auth_router.post('/reg')
async def registration(schema: AuthReg, session: AsyncSession = Depends(get_session)):
    #Ищем запись по введённой почте
    #same_student = await select_record_by_email(email=schema.email, model=Student, session=session)
    result = await session.execute(
        select(Student).where(Student.email == schema.email)
    )
    same_student = result.scalar_one_or_none()

    #Проверяем, есть ли уже аккаунт с такой почтой
    if same_student is not None:
        raise HTTPException(status_code=409, detail='Email already taken')
    
    #Хэшируем пароль
    password = hash_password(schema.password)

    #Собираем данные, которые, будем отправлять в БД
    user_data = AuthUserCreate(
        hashed_password=password,
        role='student'
    )
    #Отправляем данные и сразу же получаем объект(чтобы использовать его id)
    user = await create_record(model=User, schema=user_data, session=session)

    #Собираем данные, которые, будем отправлять в БД
    student_data = AuthStudentCreate(
        user_id=user.user_id,
        email=schema.email,
        first_name=schema.first_name,
        last_name=schema.last_name
    )
    #Отправляем данные
    await create_record(model=Student, schema=student_data, session=session)

    return {'message': 'New account successfully created'}

@auth_router.post('/login')
async def login(schema: AuthLogin, session: AsyncSession = Depends(get_session)):
    #Сначала ищем запись в students по почте, берём user_id и сразу достаёт строку с таким user_id из users(склеили строчки из students и users в одну) 
    result = await session.execute(
        select(Student).options(joinedload(Student.user)).where(Student.email == schema.email)
    )
    same_student = result.scalar_one_or_none()

    # result = await session.execute(
    #     select(Student).where(Student.email == schema.email)
    # )
    # same_student = result.scalar_one_or_none()

    #Проверяем, есть ли уже аккаунт с такой почтой
    if same_student is None:
        raise HTTPException(status_code=401, detail='Account with this email does not exists')
    
    #Ищем запись по id и сразу сохраняем объект для дальнейшей работы
    user = same_student.user #await select_record(id=same_student.user_id, model=User, session=session)

    #Сравниваем хэш введённого пароля с хэшем из БД
    is_verified = verify_password(password_plain=schema.password, password_hashed=user.hashed_password)

    if is_verified:
        #Создаём JWT токен
        token = create_access_token({'sub': str(user.user_id), 'role': user.role})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail='Password is wrong')