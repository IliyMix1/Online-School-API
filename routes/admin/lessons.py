#Для эндпоинтов
from fastapi                import APIRouter, Depends, HTTPException
from schemas.schemas        import LessonCreate
#Для интеграции с PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy             import select
from database               import get_session, create_record
from models.models          import Lesson, Attendance
#Зависимости
from dependencies           import get_current_user, get_current_admin, get_enrollment

admin_router = APIRouter(prefix='/admin', tags=['Lessons'])

@admin_router.post('/lessons')
async def create_lesson(schema: LessonCreate, admin = Depends(get_current_admin), session: AsyncSession = Depends(get_session)):
    return await create_record(model=Lesson, schema=schema, session=session)