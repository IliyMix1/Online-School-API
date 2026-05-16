from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session, select_all_records, select_record, create_record, patch_record
from models.models import User, Student, Course, Enrollment, Homework, Lesson, Submission, Attendance
from schemas.schemas import AuthReg, AuthLogin, AuthUserCreate, AuthStudentCreate, EnrollmentCreate, EnrollmentBuy, SubmissionHomework, AttendanceLesson
from auth import verify_password, hash_password, create_access_token
from dependencies import get_current_user, get_enrollment

my_router = APIRouter(prefix='/my', tags=['Lessons'])

@my_router.get('/courses/{course_id}/lessons')
async def get_lessons_by_course(course_id: int, user = Depends(get_current_user), enrollment = Depends(get_enrollment), session: AsyncSession = Depends(get_session)):
    #Ищем записи в БД по id курса
    result = await session.execute(
        select(Lesson).where(Lesson.course_id == course_id)
    )
    lessons = result.scalars().all()

    return lessons

@my_router.get('/lessons/{lesson_id}')
async def get_lesson(lesson_id: int, session: AsyncSession = Depends(get_session), user = Depends(get_current_user)):
    #Проверяем есть ли такой урок
    result = await session.execute(
        select(Lesson).where(Lesson.lesson_id == lesson_id)
    )
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail='Lesson not found')
    
    #Проверяем достаточно ли у пользователя прав, чтобы посмотреть этот урок
    enrollment = await get_enrollment(course_id=lesson.course_id, user=user, session=session)
    
    return lesson

@my_router.post('/lessons/{lesson_id}/attend')
async def attend_lesson(lesson_id: int, session: AsyncSession = Depends(get_session), user = Depends(get_current_user)):
    #Проверяем есть ли такой урок
    result = await session.execute(
        select(Lesson).where(Lesson.lesson_id == lesson_id)
    )
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail='Lesson not found')
    
    #Проверяем достаточно ли у пользователя прав, чтобы посмотреть этот урок
    enrollment = await get_enrollment(course_id=lesson.course_id, user=user, session=session)

    attendance_data = AttendanceLesson(
        enrollment_id=enrollment.enrollment_id,
        lesson_id=lesson_id
    )

    return await create_record(model=Attendance, schema=attendance_data, session=session)