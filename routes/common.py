from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session, select_all_records, select_record, create_record, patch_record
from models.models import User, Student, Course, Enrollment, Homework, Lesson, Submission, Attendance
from schemas.schemas import AuthReg, AuthLogin, AuthUserCreate, AuthStudentCreate, EnrollmentCreate, EnrollmentBuy, SubmissionHomework, AttendanceLesson
from auth import verify_password, hash_password, create_access_token
from dependencies import get_current_user, get_enrollment

router = APIRouter()


@router.get('/my/enrollments', tags=['Courses'])
async def get_owned_courses(session: AsyncSession = Depends(get_session), user = Depends(get_current_user)):
    result = await session.execute(
        select(Enrollment).where(Enrollment.user_id == user.user_id)
        )
    return result.scalars().all()