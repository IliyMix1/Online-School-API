from sqlalchemy             import select
from sqlalchemy.orm         import sessionmaker
from sqlalchemy.pool        import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import os
from dotenv import load_dotenv

#Загружаем переменные из .env
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_URL_TEST = os.getenv('DATABASE_URL_TEST')

#Создаём асинхронный движок для самого приложения и для тестов
engine = create_async_engine(DATABASE_URL)
engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool )

#Создаём сессии для самого приложения и для тестов
async_session = sessionmaker(engine, class_=AsyncSession)
async_session_test = sessionmaker(engine_test, class_=AsyncSession)

#Создаём функции получения сессии для самого приложения и для тестов
async def get_session():
    #Создаём асинхронную сессию и кладём её в переменную(with - гарантирует, что она сама закроется после работы с сессией)
    async with async_session() as session:
        yield session

async def get_session_test():
    #Создаём асинхронную сессию и кладём её в переменную(with - гарантирует, что она сама закроется после работы с сессией)
    async with async_session_test() as session:
        yield session


async def select_all_records(model, session: AsyncSession):
    '''Отображаем все записи из таблице'''
    record = await session.execute(select(model))
    return record.scalars().all()

async def select_record(id, model, session: AsyncSession):
    '''Отображаем конкретную запись из таблицы по id(PRIMARY KEY)'''
    #Получаем запись из БД по id(primary key)
    record = await session.get(model, id)
    return record

async def create_record(model, schema, session: AsyncSession):
    '''Создаём запись в таблице'''
    new_record = model(**schema.model_dump())

    session.add(new_record)
    await session.commit()
    await session.refresh(new_record)

    return new_record


async def patch_record(id: int, model, schema, session: AsyncSession):
    '''Частично изменяем запись в таблице'''
    #Получаем запись из БД по id(primary key)
    record = await session.get(model, id)

    #Проверяем существует ли такая запись
    if record is None:
        return None

    #Находим те столбцы, которые были в запросе и изменяем их(пустые - пропускаем)    
    for key, value in schema.model_dump(exclude_unset=True).items():
        setattr(record, key, value)

    await session.commit()
    await session.refresh(record)
    return record
