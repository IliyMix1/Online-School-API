from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session, select_all_records, select_record, create_record, patch_record
from models.models import User, Student, Course, Enrollment, Homework, Lesson, Submission, Attendance
from schemas.schemas import AuthReg, AuthLogin, AuthUserCreate, AuthStudentCreate, EnrollmentCreate, EnrollmentBuy, SubmissionHomework, AttendanceLesson
from auth import verify_password, hash_password, create_access_token
from dependencies import get_current_user, get_enrollment

router = APIRouter()

@router.get('/{course_id}/homeworks', tags=['Homeworks'])
async def get_homeworks_by_course(course_id: int, user = Depends(get_current_user), enrollment = Depends(get_enrollment), session: AsyncSession = Depends(get_session)):
    #Ищем записи в БД по id курса
    result = await session.execute(
        select(Homework).where(Homework.course_id == course_id)
    )
    homeworks = result.scalars().all()

    return homeworks


@router.get('/homeworks/{homework_id}', tags=['Homeworks'])
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

@router.post('/homeworks/{homework_id}/submit', tags=['Homeworks'])
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



@router.get('/{course_id}/lessons', tags=['Lessons'])
async def get_lessons_by_course(course_id: int, user = Depends(get_current_user), enrollment = Depends(get_enrollment), session: AsyncSession = Depends(get_session)):
    #Ищем записи в БД по id курса
    result = await session.execute(
        select(Lesson).where(Lesson.course_id == course_id)
    )
    lessons = result.scalars().all()

    return lessons

@router.get('/lessons/{lesson_id}', tags=['Lessons'])
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

@router.get('/lessons/{lesson_id}/attend', tags=['Lessons'])
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




# @router.get('/submissions')
# async def get_submissions(session: AsyncSession = Depends(get_session)):
#     return await select_all_records(model=Submission, session=session)

@router.get('/{enrollment_id}/submissions')
async def get_submissions_by_enrollment(enrollment_id: int, user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    #Проверяем есть ли такой id в БД
    result = await session.execute(
        select(Enrollment).where(Enrollment.enrollment_id == enrollment_id)
    )
    enrollment = result.scalar_one_or_none()
    
    if enrollment is None:
        raise HTTPException(status_code=404, detail='Enrollment not found')

    if enrollment.user_id != user.user_id:
        raise HTTPException(status_code=403, detail='Course is not owned')

    #Достаём из БД все сданные работы по id
    result = await session.execute(
        select(Submission).where(Submission.enrollment_id == enrollment_id)
    )
    submissions = result.scalars().all()
    return submissions

@router.get('/{enrollment_id}/attendance')
async def get_attendance_by_enrollment(enrollment_id: int, user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    #Проверяем есть ли такой id в БД
    result = await session.execute(
        select(Enrollment).where(Enrollment.enrollment_id == enrollment_id)
    )
    enrollment = result.scalar_one_or_none()

    if enrollment is None:
        raise HTTPException(status_code=404, detail='Enrollment not found')

    if enrollment.user_id != user.user_id:
        raise HTTPException(status_code=403, detail='Course is not owned')

    result = await session.execute(
        select(Attendance).where(Attendance.enrollment_id == enrollment_id)
    )
    attendance = result.scalar_one_or_none()
    return attendance


@router.post('/reg', tags=['Auth'])
async def registration(schema: AuthReg, session: AsyncSession = Depends(get_session)):
    #Ищем запись по введённой почте
    #same_student = await select_record_by_email(email=schema.email, model=Student, session=session)
    result = await session.execute(
        select(Student).where(Student.email == schema.email)
    )
    same_student = result.scalar_one_or_none()

    #Проверяем, есть ли уже аккаунт с такой почтой
    if same_student is not None:
        raise HTTPException(status_code=409, detail='Email already taken')
    
    #Хэшируем пароль
    password = hash_password(schema.password)

    #Собираем данные, которые, будем отправлять в БД
    user_data = AuthUserCreate(
        hashed_password=password,
        role='student'
    )
    #Отправляем данные и сразу же получаем объект(чтобы использовать его id)
    user = await create_record(model=User, schema=user_data, session=session)

    #Собираем данные, которые, будем отправлять в БД
    student_data = AuthStudentCreate(
        user_id=user.user_id,
        email=schema.email,
        first_name=schema.first_name,
        last_name=schema.last_name
    )
    #Отправляем данные
    await create_record(model=Student, schema=student_data, session=session)

    return {'message': 'New account successfully created'}

@router.post('/login', tags=['Auth'])
async def login(schema: AuthLogin, session: AsyncSession = Depends(get_session)):
    #Ищем запись по введённой почте
    #same_student = await select_record_by_email(email=schema.email, model=Student, session=session)
    result = await session.execute(
        select(Student).where(Student.email == schema.email)
    )
    same_student = result.scalar_one_or_none()

    #Проверяем, есть ли уже аккаунт с такой почтой
    if same_student is None:
        raise HTTPException(status_code=401, detail='Account with this email does not exists')
    
    #Ищем запись по id и сразу сохраняем объект для дальнейшей работы
    user = await select_record(id=same_student.user_id, model=User, session=session)

    #Сравниваем хэш введённого пароля с хэшем из БД
    is_verified = verify_password(password_plain=schema.password, password_hashed=user.hashed_password)

    if is_verified:
        #Создаём JWT токен
        token = create_access_token({'sub': str(user.user_id), 'role': user.role})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail='Password is wrong')

@router.get('/enrollments', tags=['Courses'])
async def get_owned_courses(session: AsyncSession = Depends(get_session), user = Depends(get_current_user)):
    result = await session.execute(
        select(Enrollment).where(Enrollment.user_id == user.user_id)
        )
    return result.scalars().all()


# @router.get('/homeworks/{homework_id}', tags=['Homeworks'])
# async def get_homework(homework_id: int, session: AsyncSession = Depends(get_session), user = Depends(get_current_user)):
#     #Проверяем есть ли такая домашка в БД
#     result = await session.execute(
#         select(Homework).where(Homework.homework_id == homework_id)
#     )
#     homework = result.scalar_one_or_none()

#     if homework is None:
#         raise HTTPException(status_code=404, detail='Not found')
    
#     #Проверяем достаточно ли у пользователя прав, чтобы посмотреть эту домашку
#     result = await session.execute(
#         select(Enrollment).where(Enrollment.course_id == homework.course_id, Enrollment.user_id == user.user_id)
#     )
#     enrollment = result.scalar_one_or_none()

#     if enrollment is None:
#         raise HTTPException(status_code=403, detail='Course is not owned')

#     return homework

# @router.post('/homeworks/{homework_id}/submit', tags=['Homeworks'])
# async def submit_homework(homework_id: int, score: int, session: AsyncSession = Depends(get_session), user = Depends(get_current_user)):
#     #Проверяем есть ли такая домашка в БД
#     result = await session.execute(
#         select(Homework).where(Homework.homework_id == homework_id)
#     )
#     homework = result.scalar_one_or_none()

#     if homework is None:
#         raise HTTPException(status_code=404, detail='Not found')
    
#     #Проверяем достаточно ли у пользователя прав, чтобы посмотреть эту домашку
#     result = await session.execute(
#         select(Enrollment).where(Enrollment.course_id == homework.course_id, Enrollment.user_id == user.user_id)
#     )
#     enrollment = result.scalar_one_or_none()

#     if enrollment is None:
#         raise HTTPException(status_code=403, detail='Course is not owned')
    
#     submission_data = SubmissionHomework(
#         enrollment_id=enrollment.enrollment_id,
#         homework_id=homework_id,
#         score=score,
#     )

#     return await create_record(model=Submission, schema=submission_data, session=session)