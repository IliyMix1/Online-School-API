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
import routes.my.homeworks as my_homeworks 
import routes.my.lessons   as lessons
import routes.my.progress  as progress

import routes.admin.homeworks as admin_homeworks

from database import engine
from models.models import Base

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with engine.begin() as conn:
#         #Создаём таблицы по моделям
#         await conn.run_sync(Base.metadata.create_all)
#     yield

#Создаём объект класса
app = FastAPI()
#Подключаем роутер, где описаны эндпоинты для работы со students
#app.include_router(legacy.legacy_router)
app.include_router(auth.auth_router)
app.include_router(progress.my_router)
app.include_router(lessons.my_router)
app.include_router(my_homeworks.my_router)

app.include_router(admin_homeworks.admin_router)

#.include_router(common.router)
app.include_router(users.users_router)
app.include_router(courses.courses_router)

app.include_router(enrollments.router)

#Поднимаем сервер
if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)