#Для эндпоинтов
from fastapi                import APIRouter, Depends, HTTPException
from schemas.schemas        import HomeworkCreate
#Для интеграции с PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession
#from sqlalchemy             import select
from database               import get_session 
from models.models          import Homework, HomeworkTask
#Зависимости
from dependencies           import get_current_admin

admin_router = APIRouter(prefix='/admin', tags=['Homeworks'])

@admin_router.post('/homeworks')
async def create_homework(homework_data: HomeworkCreate, admin = Depends(get_current_admin), session: AsyncSession = Depends(get_session)):
    #Собираем данные, которые отправим в таблицу
    homework = Homework(
        course_id=homework_data.course_id,
        homework_name=homework_data.homework_name,
        deadline=homework_data.deadline,
        lesson_id=homework_data.lesson_id,
    )
    
    #Добавляем запись в таблицу с домашками, но не завершаем транзакцию
    session.add(homework)
    await session.flush()

    #Собираем список с задачами, которые необходимо внести в таблицу
    homework_tasks = []
    for task_id in homework_data.task_ids:
        homework_tasks.append(HomeworkTask(
            homework_id=homework.homework_id,
            task_id=task_id
        ))
    #Делаем bulk-операцию и разом добавляем кучу записей в БД
    session.add_all(homework_tasks)

    #Завершаем транзакцию
    await session.commit()
    await session.refresh(homework)

