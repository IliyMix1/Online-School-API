from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session, select_all_records, select_record, create_record, patch_record
from models.models import User, Student, Course, Enrollment, Homework, Lesson, Submission, Attendance
from schemas.schemas import AuthReg, AuthLogin, AuthUserCreate, AuthStudentCreate, EnrollmentCreate, EnrollmentBuy, SubmissionHomework, AttendanceLesson
from auth import verify_password, hash_password, create_access_token
from dependencies import get_current_user, get_enrollment

my_router = APIRouter(prefix='/my', tags=['Homeworks'])


@my_router.get('/courses/{course_id}/homeworks')
async def get_homeworks_by_course(course_id: int, user = Depends(get_current_user), enrollment = Depends(get_enrollment), session: AsyncSession = Depends(get_session)):
    #Ищем записи в БД по id курса
    result = await session.execute(
        select(Homework).where(Homework.course_id == course_id)
    )
    homeworks = result.scalars().all()

    return homeworks


@my_router.get('/homeworks/{homework_id}')
async def get_homework(homework_id: int, session: AsyncSession = Depends(get_session), user = Depends(get_current_user)):
    #Проверяем есть ли такая домашка в БД
    result = await session.execute(
        select(Homework).where(Homework.homework_id == homework_id)
    )
    homework = result.scalar_one_or_none()

    if homework is None:
        raise HTTPException(status_code=404, detail='Homework not found')
    
    #Проверяем достаточно ли у пользователя прав, чтобы посмотреть эту домашку
    enrollment = await get_enrollment(course_id=homework.course_id, user=user, session=session)

    return homework

@my_router.post('/homeworks/{homework_id}/submit')
async def submit_homework(homework_id: int, score: int, session: AsyncSession = Depends(get_session), user = Depends(get_current_user)):
    #Проверяем есть ли такая домашка в БД
    result = await session.execute(
        select(Homework).where(Homework.homework_id == homework_id)
    )
    homework = result.scalar_one_or_none()

    if homework is None:
        raise HTTPException(status_code=404, detail='Not found')
    
    #Проверяем достаточно ли у пользователя прав, чтобы посмотреть эту домашку
    enrollment = await get_enrollment(course_id=homework.course_id, user=user, session=session)
    
    submission_data = SubmissionHomework(
        enrollment_id=enrollment.enrollment_id,
        homework_id=homework_id,
        score=score,
    )

    return await create_record(model=Submission, schema=submission_data, session=session)