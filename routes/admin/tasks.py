#Для эндпоинтов
from fastapi                import APIRouter, Depends, HTTPException
from schemas.schemas        import TaskCreate, TaskPatch
#Для интеграции с PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy             import select
from database               import get_session, create_record, patch_record
from models.models          import Homework, HomeworkTask, Course, Lesson, Task
#Зависимости
from dependencies           import get_current_admin

admin_router = APIRouter(prefix='/admin', tags=['Tasks'])

@admin_router.post('/tasks')
async def create_task(schema: TaskCreate, admin = Depends(get_current_admin), session: AsyncSession = Depends(get_session)):
    return await create_record(model=Task, schema=schema, session=session)

@admin_router.patch('/tasks/{task_id}')
async def patch_task(task_id: int, schema: TaskPatch, admin = Depends(get_current_admin), session: AsyncSession = Depends(get_session)):
    return await patch_record(id=task_id, model=Task, schema=schema, session=session)