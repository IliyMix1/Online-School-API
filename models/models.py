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
    student:    Mapped['Student']    = relationship('Student', back_populates='user', uselist=False)
    enrollment: Mapped['Enrollment'] = relationship('Enrollment', back_populates='user', uselist=False)


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
    enrollment: Mapped['Enrollment'] = relationship('Enrollment', back_populates='course', uselist=False)
    homework:   Mapped['Homework']   = relationship('Homework',   back_populates='course', uselist=False)
    lesson:     Mapped['Lesson']     = relationship('Lesson',     back_populates='course', uselist=False)

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
    user:       Mapped['User']       = relationship('User',       back_populates='enrollment', uselist=False)
    course:     Mapped['Course']     = relationship('Course',     back_populates='enrollment', uselist=False)
    submission: Mapped['Submission'] = relationship('Submission', back_populates='enrollment', uselist=False)
    attendance: Mapped['Attendance'] = relationship('Attendance', back_populates='enrollment', uselist=False)

class Homework(Base):
    __tablename__ = 'homeworks'

    #Описываем колонки таблицы
    homework_id:   Mapped[int]   = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    course_id:     Mapped[int]   = mapped_column(BigInteger, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    homework_name: Mapped[str]   = mapped_column(String(50), nullable=False, unique=True)
    max_score:     Mapped[int]   = mapped_column(SmallInteger, nullable=False)
    deadline:      Mapped[date]  = mapped_column(Date, nullable=False)
    created_at:    Mapped[date]  = mapped_column(Date, nullable=False, server_default=func.now())
    lesson_id:     Mapped[int]   = mapped_column(BigInteger, ForeignKey('lessons.lesson_id', ondelete='CASCADE'), nullable=True)

    #Описываем связи с другими таблицами
    course:     Mapped['Course']     = relationship('Course',     back_populates='homework', uselist=False)
    submission: Mapped['Submission'] = relationship('Submission', back_populates='homework', uselist=False)
    lesson:     Mapped['Lesson']     = relationship('Lesson',     back_populates='homework', uselist=False)

class Lesson(Base):
    __tablename__ = 'lessons'

    #Описываем колонки таблицы
    lesson_id:   Mapped[int]   = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    course_id:   Mapped[int]   = mapped_column(BigInteger, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    lesson_name: Mapped[str]   = mapped_column(String(50), nullable=False, unique=True)
    lesson_date: Mapped[date]  = mapped_column(Date, nullable=False)
    created_at:  Mapped[date]  = mapped_column(Date, nullable=False, server_default=func.now())

    #Описываем связи с другими таблицами
    course:      Mapped['Course']     = relationship('Course',     back_populates='lesson', uselist=False)
    attendance:  Mapped['Attendance'] = relationship('Attendance', back_populates='lesson', uselist=False)
    homework:    Mapped['Homework']   = relationship('Homework',   back_populates='lesson', uselist=False)

class Submission(Base):
    __tablename__ = 'submissions'

    #Описываем колонки таблицы
    submission_id:   Mapped[int]  = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    enrollment_id:   Mapped[int]  = mapped_column(BigInteger, ForeignKey('enrollments.enrollment_id', ondelete='CASCADE'), nullable=False)
    homework_id:     Mapped[int]  = mapped_column(BigInteger, ForeignKey('homeworks.homework_id', ondelete='CASCADE'), nullable=False)
    score:           Mapped[int]  = mapped_column(SmallInteger, nullable=False)
    submission_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    #Описываем связи с другими таблицами
    enrollment: Mapped['Enrollment'] = relationship('Enrollment', back_populates='submission', uselist=False)
    homework:   Mapped['Homework']   = relationship('Homework', back_populates='submission', uselist=False)

class Attendance(Base):
    __tablename__ = 'attendance'

    #Описываем колонки таблицы
    attendance_id:   Mapped[int]  = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    enrollment_id:   Mapped[int]  = mapped_column(BigInteger, ForeignKey('enrollments.enrollment_id', ondelete='CASCADE'), nullable=False)
    lesson_id:       Mapped[int]  = mapped_column(BigInteger, ForeignKey('lessons.lesson_id', ondelete='CASCADE'), nullable=False)
    attendance_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    
    #Описываем связи с другими таблицами
    enrollment: Mapped['Enrollment'] = relationship('Enrollment', back_populates='attendance', uselist=False)
    lesson:     Mapped['Lesson']     = relationship('Lesson',     back_populates='attendance', uselist=False)