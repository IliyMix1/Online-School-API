from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session, select_all_records, select_record, create_record, patch_record
from models.models import User, Student, Course, Enrollment, Homework, Lesson, Submission, Attendance
from schemas.schemas import UserCreate, UserPatch, CourseCreate, CoursePatch, CourseOut, EnrollmentBuy, EnrollmentCreate
from dependencies import get_current_user, get_current_admin


courses_router = APIRouter(tags=['Courses'])


@courses_router.get('/courses', response_model=list[CourseOut])
async def get_all_courses(session: AsyncSession = Depends(get_session)):
    #Вызываем асинхронную функцию, чтобы посмотреть всю таблицу
    return await select_all_records(model=Course, session=session)


@courses_router.get('/courses/{course_id}', response_model=CourseOut)
async def get_course(course_id: int, session: AsyncSession = Depends(get_session)):
    record = await select_record(id=course_id, model=Course, session=session)

    if record is None:
        raise HTTPException(status_code=404, detail='Record not found')

    return record


@courses_router.post('/courses/{course_id}')
async def buy_course(course_id: int, schema: EnrollmentBuy, session: AsyncSession = Depends(get_session), user = Depends(get_current_user)):
    #Проверяем существует ли желаемый курс
    #course = await select_record(id=course_id, model=Course, session=session)
    result = await session.execute(
        select(Course).where(Course.course_id == course_id)
    )
    course = result.scalar_one_or_none()

    if course is None:
        raise HTTPException(status_code=404, detail='Course not found')
    
    #Проверяем, покупал ли уже человек этот курс раньше
    #record = await select_record_by_user_id_course_id(user_id=user.user_id, course_id=course_id, model=Enrollment, session=session)
    result = await session.execute(
        select(Enrollment).where(Enrollment.user_id == user.user_id, Enrollment.course_id == course_id)
    )
    record = result.scalar_one_or_none()

    if record is not None:
        raise HTTPException(status_code=409, detail='Course is already owned')

    #Собираем данные, чтобы сделать запись в БД
    data = EnrollmentCreate(
        user_id=user.user_id,
        course_id=course_id,
        tariff=schema.tariff,
        status='active',
    )

    return await create_record(model=Enrollment, schema=data, session=session)


@courses_router.post('/admin/courses', response_model=CourseOut)
async def create_course(course: CourseCreate, session: AsyncSession = Depends(get_session), user = Depends(get_current_admin)):
    return await create_record(schema=course, model=Course, session=session)

@courses_router.patch('/admin/courses/{course_id}', response_model=CourseOut)
async def patch_course(course_id: int, data: CoursePatch, session: AsyncSession = Depends(get_session), user = Depends(get_current_admin)):
    record = await patch_record(id=course_id, model=Course, schema=data, session=session)

    if record is None:
        raise HTTPException(status_code=404, detail='Record not found')
    
    return record