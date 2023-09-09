from fastapi import Depends, Request
from jose import ExpiredSignatureError, JWTError, jwt

from app.config import settings
from app.exceptions import (
    IncorrectFormatTokenException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.users.dao import UserDAO
from app.users.models import Users


def get_token(request: Request):
    token = request.cookies.get('booking_access_token')
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.SECRET_ALGORITHM
        )
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError:
        raise IncorrectFormatTokenException
    user_id: str = payload.get('sub')
    if not user_id:
        raise UserIsNotPresentException
    user = await UserDAO.find_one_or_none(id=int(user_id))
    if not user:
        raise UserIsNotPresentException
    return user


async def get_current_admin_user(current_admin_user: Users = Depends(get_current_user)):
    # if current_admin_user.role != 'admin':
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return current_admin_user