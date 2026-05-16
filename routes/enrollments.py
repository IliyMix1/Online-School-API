from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session, select_all_records, select_record, create_record, patch_record
from models.models import User, Student, Course, Enrollment, Homework, Lesson, Submission, Attendance
from schemas.schemas import EnrollmentCreate, EnrollmentPatch, EnrollmentOut
from dependencies import get_current_admin

router = APIRouter(tags=['Enrollments'])


@router.get('/admin/enrollments', response_model=list[EnrollmentOut])
async def get_all_enrollments(session: AsyncSession = Depends(get_session), admin = Depends(get_current_admin)):
    return await select_all_records(model=Enrollment, session=session)


@router.get('/admin/enrollments/{enrollment_id}', response_model=EnrollmentOut)
async def get_enrollment(enrollment_id: int, session: AsyncSession = Depends(get_session), admin = Depends(get_current_admin)):
    record = await select_record(id=enrollment_id, model=Enrollment, session=session)

    if record is None:
        raise HTTPException(status_code=404, detail='Record not found')
    
    return record

@router.post('/admin/enrollments', response_model=EnrollmentOut)
async def create_enrollment(enrollment_data: EnrollmentCreate, session: AsyncSession = Depends(get_session), admin = Depends(get_current_admin)):
    #Проверяем существует ли уже такой enrollment
    result = await session.execute(
        select(Enrollment).where(Enrollment.user_id == enrollment_data.user_id, Enrollment.course_id == enrollment_data.course_id)
    )
    enrollment = result.scalar_one_or_none()

    if enrollment is not None:
        raise HTTPException(status_code=409, detail='Enrollment already exists')
    
    #Проверяем существует лм такой ученик
    result = await session.execute(
        select(User).where(User.user_id == enrollment_data.user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    #Проверяем существует ли такой курс
    result = await session.execute(
        select(Course).where(Course.course_id == enrollment_data.course_id)
    )
    course = result.scalar_one_or_none()

    if course is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    #После всех проверок - создаём запись в таблице
    record = await create_record(model=Enrollment, schema=enrollment_data, session=session)
    return record


@router.patch('/admin/enrollments/{enrollment_id}')
async def patch_enrollment(enrollment_id: int, enrollment_data: EnrollmentPatch, session: AsyncSession = Depends(get_session), admin = Depends(get_current_admin)):
    #Проверяем существует ли уже такой enrollment
    # result = await session.execute(
    #     select(Enrollment).where(Enrollment.enrollment_id == enrollment_id)
    # )
    # enrollment = result.scalar_one_or_none()

    # if enrollment is None:
    #     raise HTTPException(status_code=404, detail='Enrollment not found')
    
    record = await patch_record(id=enrollment_id, model=Enrollment, schema=enrollment_data, session=session)
    if record is None:
        raise HTTPException(status_code=404, detail='Enrollment not found')
    return record


# #НАДО ССЫЛАТЬСЯ НА STUDENTS, А НЕ USERS
# @enrollments_router.patch('/{enrollment_id}', response_model=EnrollmentOut)
# async def patch_enrollment(enrollment_id: int, schema: EnrollmentPatch, session: AsyncSession = Depends(get_session)):
#     #Валидируем id юзера
#     user = await session.get(User, schema.user_id)
#     if user is None:
#         raise HTTPException(status_code=404, detail='User not found')
    
#     #Валидируем id курса
#     course = await session.get(User, schema.course_id)
#     if course is None:
#         raise HTTPException(status_code=404, detail='Course not found')
    
#     return await patch_record(id=enrollment_id, model=Enrollment, schema=schema, session=session)