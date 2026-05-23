#Для эндпоинтов
from fastapi                import APIRouter, Depends, HTTPException
from schemas.schemas        import HomeworkCreate
#Для интеграции с PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy             import select
from database               import get_session 
from models.models          import Homework, HomeworkTask, Course, Lesson, Task
#Зависимости
from dependencies           import get_current_admin

admin_router = APIRouter(prefix='/admin', tags=['Homeworks'])

@admin_router.post('/homeworks')
async def create_homework(homework_data: HomeworkCreate, admin = Depends(get_current_admin), session: AsyncSession = Depends(get_session)):
    #Проверяем существует ли такой курс
    result = await session.execute(
        select(Course).where(Course.course_id == homework_data.course_id)
    )
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(status_code=404, detail='Course not found')

    #Запускаем проверки, если был передан id урока
    if homework_data.lesson_id is not None:
        #Проверяем существует ли такой урок
        result = await session.execute(
            select(Lesson).where(Lesson.lesson_id == homework_data.lesson_id)
        )
        lesson = result.scalar_one_or_none()
        if lesson is None:
            raise HTTPException(status_code=404, detail='Lesson not found')
        
        #Проверяем принадлежит ли урок к нужному курсу
        if lesson.course_id != homework_data.course_id:
            raise HTTPException(status_code=409, detail='Lesson does not belong to this course')
    
    #Получаем все уникальные id задач и проверяем какие из них есть в БД
    submitted_task_ids = set(homework_data.task_ids)
    result = await session.execute(
        select(Task.task_id).where(Task.task_id.in_(submitted_task_ids))
    )
    #Получаем все уникальные id задач, которые есть в БД
    existing_task_ids = set(result.scalars().all())

    if (submitted_task_ids - existing_task_ids):
        raise HTTPException(status_code=404, detail='Some task ids were not found')

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

