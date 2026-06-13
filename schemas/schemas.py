from typing import Literal
from pydantic import BaseModel, field_validator, Field
from datetime import date

class AuthReg(BaseModel):
    '''Для регистрации'''
    first_name: str = Field(max_length=50)
    last_name:  str = Field(max_length=50)
    email:      str = Field(max_length=320)
    password:   str = Field(min_length=8, max_length=70)

class AuthLogin(BaseModel):
    '''Для логина'''
    email:    str = Field(max_length=320)
    password: str = Field(min_length=8, max_length=70)

class AuthUserCreate(BaseModel):
    '''Для создания записи в таблице с хэшами при регистрации'''
    hashed_password: str 
    role: Literal['student', 'admin']

class AuthStudentCreate(BaseModel):
    '''Для создания записи в таблице с контактной информацией при регистрации'''
    user_id:    int
    email:      str = Field(max_length=320)
    first_name: str = Field(max_length=50)
    last_name:  str = Field(max_length=50)


class UserCreate(BaseModel):
    '''Для создания записи в таблице с хэшами вручную'''
    hashed_password: str = Field(min_length=2)
    role: Literal['student', 'admin']

class UserPatch(BaseModel):
    '''Для изменения пароля или роли'''
    hashed_password: str | None = None
    role: Literal['student', 'admin'] | None = None

class UserOut(BaseModel):
    user_id: int
    role: str
    created_at: date


class StudentOut(BaseModel):
    '''Для отображения контактной информации ученика'''
    first_name:   str
    last_name:    str
    email:        str
    phone_number: str | None = None

class StudentPatch(BaseModel):
    '''Для точечного изменения контактной информации ученика'''
    first_name:   str | None = None
    last_name:    str | None = None
    email:        str | None = None
    phone_number: str | None = None


class CourseCreate(BaseModel):
    '''Для создания курса'''
    name: str = Field(min_length=2)

class CoursePatch(BaseModel):
    '''Для точечного изменения курса'''
    name: str | None = None

class CourseOut(CourseCreate):
    '''Для отображения курса'''
    course_id:  int
    created_at: date


class EnrollmentBuy(BaseModel):
    '''Для покупки курса'''
    tariff:     Literal['mini', 'standard', 'pro']

class EnrollmentCreate(BaseModel):
    '''Для создания записи после покупки курса'''
    user_id:    int
    course_id:  int
    tariff:     Literal['mini', 'standard', 'pro']
    status:     Literal['active', 'finished', 'quit']

class EnrollmentPatch(BaseModel):
    '''Для точечного изменения данных в купленных курсах ученика'''
    course_id: int  | None = None
    tariff:    Literal['mini', 'standard', 'pro']    | None = None
    status:    Literal['active', 'finished', 'quit'] | None = None
    ended_at:  date | None = None

class EnrollmentOut(EnrollmentCreate):
    '''Для отображения купленного курса'''
    enrollment_id: int
    created_at:    date
    ended_at:      date | None


class SubmissionHomework(BaseModel):
    '''Для записи в таблицу всех сданных работ'''
    enrollment_id: int
    homework_id:   int
    score:         int


class AttendanceLesson(BaseModel):
    '''Для записи в таблицу с посещаемостью'''
    enrollment_id: int
    lesson_id:     int

class LessonCreate(BaseModel):
    '''Для создания уроков'''
    course_id:   int
    lesson_name: str
    lesson_date: date

class LessonPatch(BaseModel):
    course_id:   int | None = None
    lesson_name: str | None = None
    lesson_date: date | None = None


class TaskForStudent(BaseModel):
    '''Для отображения заданий'''
    task_id:   int
    task_text: str
    points:    int


class TaskSubmit(BaseModel):
    '''Для сдачи заданий'''
    task_id: int
    answer: str = Field(min_length=1)
    
class HomeworkCreate(BaseModel):
    course_id:     int
    homework_name: str
    deadline:      date
    lesson_id:     int | None = None
    task_ids:      list[int]

class HomeworkPatch(BaseModel):
    course_id:     int       | None = None
    homework_name: str       | None = None
    deadline:      date      | None = None
    lesson_id:     int       | None = None
    #task_ids:      list[int] | None = None