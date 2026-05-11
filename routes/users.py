from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session, select_all_records, create_record, patch_record
from models.models import User, Student, Course, Enrollment, Homework, Lesson, Submission, Attendance
from schemas.schemas import UserCreate, UserPatch

users_router = APIRouter(prefix='/users', tags=['Users'])


@users_router.get('/')
async def get_users(session: AsyncSession = Depends(get_session)):
    #Вызываем асинхронную функцию, чтобы посмотреть всю таблицу
    return await select_all_records(model=User, session=session)


# @users_router.post('/')
# async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
#     return await create_record(schema=user, model=User, session=session)


@users_router.patch('/{user_id}')
async def patch_user(user_id: int, data: UserPatch, session: AsyncSession = Depends(get_session)):
    record = await patch_record(id=user_id, schema=data, model=User, session=session)
    #Проверяем есть ли вообще такая запись
    if record is None:
        raise HTTPException(status_code=404, detail='Record not found')
    return record
