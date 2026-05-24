from typing import Literal
from pydantic import BaseModel, field_validator, Field
from datetime import date

#Создаём шаблон класс, для удобства работы со студентом
# class LegacyBase(BaseModel):
#     name:   str = Field(min_length=2, max_length=50)
#     grade:  Literal[9, 10, 11]
#     tariff: Literal['mini', 'standard', 'pro']

#     @field_validator('name')
#     @classmethod
#     def validate_name(cls, value: str) -> str:
#         value = value.strip()
#         #Проверяем, не стала ли строка пустой после удаления лишних пробелов
#         if len(value) < 2:
#             raise ValueError('First name should not be empty')
        
#         #Проверяем, есть ли в имени цифры
#         for symbol in value:
#             if symbol.isdigit():
#                 raise ValueError('First name should not contain digits')
#         return value
    
# #Вариация класса для работы с выводом
# class LegacyOut(LegacyBase):
#     id: int

# #Вариация класса для создания студента
# class LegacyCreate(LegacyBase):
#     pass

# #Вариация класса для ПОЛНОГО изменения информации о студенте
# class LegacyPut(LegacyBase):
#     pass

# #Вариация класса для ЧАСТИЧНОГО изменения информации о студенте
# class LegacyPatch(BaseModel):
#     #Наши переменные имеют либо INT/STR тип, либо None, а по умолчанию все они равны None
#     name:   str | None = None
#     grade:  Literal[9, 10, 11] | None = None
#     tariff: Literal['mini', 'standard', 'pro'] | None = None

#     @field_validator('name')
#     @classmethod
#     def validate_name(cls, value: str) -> str:
#         if value is None:
#             return value
        
#         value = value.strip()
#         #Проверяем, не стала ли строка пустой после удаления лишних пробелов
#         if len(value) < 2:
#             raise ValueError('Name should not be empty')

#         #Проверяем, есть ли в имени цифры
#         for symbol in value:
#             if symbol.isdigit():
#                 raise ValueError('Name should not contain digits')
#         return value


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


class TaskForStudent(BaseModel):
    '''Для отображения заданий'''
    task_id:   int
    task_text: str
    points:    int


class TaskSubmit(BaseModel):
    '''Для сдачи заданий'''
    task_id: int
    answer: str = Field(min_length=1)

class HomeworkSubmit(BaseModel):
    '''Для сдачи домашек'''
    list[TaskSubmit]
    
class HomeworkCreate(BaseModel):
    course_id:     int
    homework_name: str
    deadline:      date
    lesson_id:     int | None = None
    #homework_id:   int
    task_ids:      list[int]