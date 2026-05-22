from sqlalchemy import Text, BigInteger, SmallInteger, Date, DateTime, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

from datetime import date, datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    #Описываем колонки таблицы
    user_id:         Mapped[int]  = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    hashed_password: Mapped[str]  = mapped_column(Text, nullable=False)
    role:            Mapped[str]  = mapped_column(Text, nullable=False)
    created_at:      Mapped[date] = mapped_column(Date, server_default=func.now())

    #Описываем связи с другими таблицами
    student:     Mapped['Student']    = relationship('Student', back_populates='user', uselist=False)
    enrollments: Mapped[list['Enrollment']] = relationship('Enrollment', back_populates='user')


class Student(Base):
    __tablename__ = 'students'

    #Описываем колонки таблицы
    user_id:      Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    first_name:   Mapped[str] = mapped_column(String(50),  nullable=False)
    last_name:    Mapped[str] = mapped_column(String(50),  nullable=False)
    email:        Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)

    #Описываем связи с другими таблицами
    user: Mapped['User'] = relationship('User', back_populates='student', uselist=False)

class Course(Base):
    __tablename__ = 'courses'

    #Описываем колонки таблицы
    course_id:  Mapped[int]  = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name:       Mapped[str]  = mapped_column(Text, nullable=False)
    created_at: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.now())

    #Описываем связи с другими таблицами
    enrollments: Mapped[list['Enrollment']] = relationship('Enrollment', back_populates='course')
    homeworks:   Mapped[list['Homework'] ]  = relationship('Homework',   back_populates='course')
    lessons:     Mapped[list['Lesson']  ]   = relationship('Lesson',     back_populates='course')

class Enrollment(Base):
    __tablename__ = 'enrollments'

    #Описываем колонки таблицы
    enrollment_id: Mapped[int]  = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id:       Mapped[int]  = mapped_column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    course_id:     Mapped[int]  = mapped_column(BigInteger, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    tariff:        Mapped[str]  = mapped_column(String(10), nullable=False)
    status:        Mapped[str]  = mapped_column(String(10), nullable=False)
    created_at:    Mapped[date] = mapped_column(Date, nullable=False, server_default=func.now())
    ended_at:      Mapped[date] = mapped_column(Date, nullable=True)

    #Описываем связи с другими таблицами
    user:       Mapped['User']       = relationship('User',       back_populates='enrollments', uselist=False)
    course:     Mapped['Course']     = relationship('Course',     back_populates='enrollments', uselist=False)
    submission: Mapped[list['Submission']] = relationship('Submission', back_populates='enrollments')
    attendance: Mapped[list['Attendance']] = relationship('Attendance', back_populates='enrollments')

class Homework(Base):
    __tablename__ = 'homeworks'

    #Описываем колонки таблицы
    homework_id:   Mapped[int]   = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    course_id:     Mapped[int]   = mapped_column(BigInteger, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    homework_name: Mapped[str]   = mapped_column(String(50), nullable=False, unique=True)
    #max_score:     Mapped[int]   = mapped_column(SmallInteger, nullable=False)
    deadline:      Mapped[date]  = mapped_column(Date, nullable=False)
    created_at:    Mapped[date]  = mapped_column(Date, nullable=False, server_default=func.now())
    lesson_id:     Mapped[int]   = mapped_column(BigInteger, ForeignKey('lessons.lesson_id', ondelete='CASCADE'), nullable=True)

    #Описываем связи с другими таблицами
    course:         Mapped['Course']             = relationship('Course',       back_populates='homeworks', uselist=False)
    submission:     Mapped[list['Submission']]   = relationship('Submission',   back_populates='homeworks')
    lessons:        Mapped['Lesson']             = relationship('Lesson',       back_populates='homeworks', uselist=False)
    homework_tasks: Mapped[list['HomeworkTask']] = relationship('HomeworkTask', back_populates='homework')

class Lesson(Base):
    __tablename__ = 'lessons'

    #Описываем колонки таблицы
    lesson_id:   Mapped[int]   = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    course_id:   Mapped[int]   = mapped_column(BigInteger, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    lesson_name: Mapped[str]   = mapped_column(String(50), nullable=False, unique=True)
    lesson_date: Mapped[date]  = mapped_column(Date, nullable=False)
    created_at:  Mapped[date]  = mapped_column(Date, nullable=False, server_default=func.now())

    #Описываем связи с другими таблицами
    course:      Mapped['Course']           = relationship('Course',     back_populates='lessons', uselist=False)
    attendance:  Mapped[list['Attendance']] = relationship('Attendance', back_populates='lessons')
    homeworks:   Mapped['Homework']         = relationship('Homework',   back_populates='lessons', uselist=False)

class Submission(Base):
    __tablename__ = 'submissions'

    #Описываем колонки таблицы
    submission_id:   Mapped[int]  = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    enrollment_id:   Mapped[int]  = mapped_column(BigInteger, ForeignKey('enrollments.enrollment_id', ondelete='CASCADE'), nullable=False)
    homework_id:     Mapped[int]  = mapped_column(BigInteger, ForeignKey('homeworks.homework_id', ondelete='CASCADE'), nullable=False)
    score:           Mapped[int]  = mapped_column(SmallInteger, nullable=False)
    submission_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    #Описываем связи с другими таблицами
    enrollments: Mapped['Enrollment'] = relationship('Enrollment', back_populates='submission', uselist=False)
    homeworks:   Mapped['Homework']   = relationship('Homework', back_populates='submission', uselist=False)

class Attendance(Base):
    __tablename__ = 'attendance'

    #Описываем колонки таблицы
    attendance_id:   Mapped[int]  = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    enrollment_id:   Mapped[int]  = mapped_column(BigInteger, ForeignKey('enrollments.enrollment_id', ondelete='CASCADE'), nullable=False)
    lesson_id:       Mapped[int]  = mapped_column(BigInteger, ForeignKey('lessons.lesson_id', ondelete='CASCADE'), nullable=False)
    attendance_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    
    #Описываем связи с другими таблицами
    enrollments: Mapped['Enrollment'] = relationship('Enrollment', back_populates='attendance', uselist=False)
    lessons:     Mapped['Lesson']     = relationship('Lesson',     back_populates='attendance', uselist=False)

class Task(Base):
    __tablename__ = 'tasks'

    #Описываем колонки таблицы
    task_id:        Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_text:      Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    points:         Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    #Описываем связи с другими таблицами
    homework_tasks: Mapped[list['HomeworkTask']] = relationship('HomeworkTask', back_populates='task')

class HomeworkTask(Base):
    __tablename__ = 'homework_tasks'

    #Описываем колонки таблицы
    homework_id:    Mapped[int] = mapped_column(BigInteger, ForeignKey('homeworks.homework_id', ondelete='CASCADE'), nullable=False, primary_key=True)
    task_id:        Mapped[int] = mapped_column(BigInteger, ForeignKey('tasks.task_id',         ondelete='CASCADE'), nullable=False, primary_key=True)

    #Описываем связи с другими таблицами
    homework: Mapped['Homework'] = relationship('Homework', back_populates='homework_tasks')
    task:     Mapped['Task']     = relationship('Task',     back_populates='homework_tasks')