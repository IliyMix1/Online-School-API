from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

#Импортируем эндпоинты
#import routes.legacy   as legacy
import routes.common   as common
import routes.users    as users
import routes.courses  as courses
import routes.enrollments as enrollments

import routes.auth as     auth
import routes.my.homeworks as homeworks 
import routes.my.lessons   as lessons
import routes.my.progress  as progress

from database import engine
from models.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        #Создаём таблицы по моделям
        await conn.run_sync(Base.metadata.create_all)
    yield

#Создаём объект класса
app = FastAPI(lifespan=lifespan)
#Подключаем роутер, где описаны эндпоинты для работы со students
#app.include_router(legacy.legacy_router)
app.include_router(auth.auth_router)
app.include_router(progress.my_router)
app.include_router(lessons.my_router)
app.include_router(homeworks.my_router)

app.include_router(common.router)
app.include_router(users.users_router)
app.include_router(courses.courses_router)

app.include_router(enrollments.router)

#Поднимаем сервер
if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)