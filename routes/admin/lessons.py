#Для эндпоинтов
from fastapi                import APIRouter, Depends, HTTPException
from schemas.schemas        import LessonCreate, LessonPatch
#Для интеграции с PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy             import select
from database               import get_session, create_record, patch_record
from models.models          import Lesson, Attendance
#Зависимости
from dependencies           import get_current_user, get_current_admin

admin_router = APIRouter(prefix='/admin', tags=['Lessons'])

@admin_router.post('/lessons')
async def create_lesson(schema: LessonCreate, admin = Depends(get_current_admin), session: AsyncSession = Depends(get_session)):
    return await create_record(model=Lesson, schema=schema, session=session)

@admin_router.patch('/lessons/{lesson_id}')
async def patch_lesson(lesson_id: int, schema: LessonPatch, admin = Depends(get_current_admin), session: AsyncSession = Depends(get_session)):
    return await patch_record(id=lesson_id, model=Lesson, schema=schema, session=session)