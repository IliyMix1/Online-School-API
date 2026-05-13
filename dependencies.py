from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Enrollment, User
from database import get_session, select_record
from auth import security, SECRET_KEY, ALGORITHM, JWTError, jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: AsyncSession = Depends(get_session)):
    '''Проверяет залогинен ли пользователь'''
    #Достаём токен из заголовка
    token = credentials.credentials

    try:
        #Расшифровываем jwt-токен и достаёт оттуда id
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail='Authentication required')
        
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')

    return await select_record(id=int(user_id), model=User, session=session)


async def get_enrollment(course_id: int, user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    '''Проверяем находится ли конкретный ученик на конкретном курсе'''
    result = await session.execute(
        select(Enrollment).where(Enrollment.course_id == course_id, Enrollment.user_id == user.user_id)
    )
    enrollment = result.scalar_one_or_none()
    
    if enrollment is None or enrollment.status == 'quit':
        raise HTTPException(status_code=403, detail='Course is not owned')
    
    return enrollment

async def check_role(user = Depends(get_current_user)):
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='Insufficient privileges')
    
    return user