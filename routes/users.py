from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session, select_all_records, create_record, patch_record
from models.models import User, Student, Course, Enrollment, Homework, Lesson, Submission, Attendance
from schemas.schemas import UserCreate, UserPatch
from dependencies import get_current_user, check_role

users_router = APIRouter(prefix='/users', tags=['Users'])


@users_router.get('/')
async def get_users(session: AsyncSession = Depends(get_session), user = Depends(check_role)):
    #Вызываем асинхронную функцию, чтобы посмотреть всю таблицу
    return await select_all_records(model=User, session=session)

@users_router.patch('/{user_id}')
async def patch_user(user_id: int, data: UserPatch, session: AsyncSession = Depends(get_session), user = Depends(check_role)):
    record = await patch_record(id=user_id, schema=data, model=User, session=session)
    #Проверяем есть ли вообще такая запись
    if record is None:
        raise HTTPException(status_code=404, detail='Record not found')
    return record
